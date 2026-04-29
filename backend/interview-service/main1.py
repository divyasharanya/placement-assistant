"""
Interview Service - Technical Interview Session Management
FastAPI-based microservice for managing interview sessions with real-time WebSocket support
Upgraded with OpenRouter AI for real question generation and response analysis
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from enum import Enum
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, Query, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, update
import redis.asyncio as redis

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

from database.models import (
    InterviewSession, InterviewQuestion, InterviewResponse, ResponseAnalysis,
    Resume, User, InterviewType, InterviewDifficulty, InterviewStatus, InterviewMode
)

# ==================== Configuration ====================

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/aimock")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
AI_ENGINE_URL = os.getenv("AI_ENGINE_URL", "http://ai-engine:8003")

# Read OpenRouter API key from file
_api_key_path = Path(r"D:\placement_assisstant\backend\resume-service\api.txt")
if _api_key_path.exists():
    with open(_api_key_path, "r") as f:
        OPENROUTER_API_KEY = f.read().strip()
else:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
AI_MODEL = "openai/gpt-4o-mini"  # cheap and fast via OpenRouter

# ==================== Database Setup ====================

engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# ==================== Redis Setup ====================

redis_client: Optional[redis.Redis] = None

async def get_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    return redis_client

# ==================== AI Client ====================

def get_ai_client() -> Optional[Any]:
    """Get OpenRouter AI client"""
    if not OPENROUTER_API_KEY or AsyncOpenAI is None:
        return None
    return AsyncOpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL
    )

async def call_ai(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    """Call OpenRouter AI and return response text"""
    client = get_ai_client()
    if not client:
        raise HTTPException(status_code=503, detail="AI service not configured. Check OPENROUTER_API_KEY.")

    kwargs = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 1500,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
        kwargs["temperature"] = 0

    try:
        completion = await client.chat.completions.create(**kwargs)
        return completion.choices[0].message.content or ""
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI call failed: {str(e)}")

# ==================== Pydantic Models ====================

class InterviewConfig(BaseModel):
    resume_id: Optional[UUID] = None
    target_role: str = "Software Engineer"
    difficulty: InterviewDifficulty = InterviewDifficulty.MEDIUM
    mode: InterviewMode = InterviewMode.TEXT
    focus_areas: Optional[List[str]] = None
    duration: int = 30  # minutes
    resume_context: Optional[str] = None  # parsed resume text/skills for AI context

class InterviewQuestionRequest(BaseModel):
    session_id: UUID
    question_type: str
    content: str
    difficulty_level: int = Field(ge=1, le=10)
    sequence_order: int
    time_limit_seconds: Optional[int] = None
    hints: Optional[List[str]] = None

class AnswerSubmission(BaseModel):
    question_id: UUID
    content: Optional[str] = None
    audio_url: Optional[str] = None
    code_submission: Optional[str] = None
    language_used: Optional[str] = None

class FeedbackReport(BaseModel):
    overall_score: float
    technical_accuracy: float
    communication: float
    problem_solving: float
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    skill_assessments: Dict[str, float]

# ==================== Interview State Management ====================

class InterviewState:
    INITIALIZED = "initialized"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# ==================== Interview Manager ====================

class InterviewManager:
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}

    async def create_session(
        self,
        user_id: UUID,
        config: InterviewConfig,
        db: AsyncSession
    ) -> InterviewSession:
        """Initialize interview session"""

        session = InterviewSession(
            user_id=user_id,
            resume_id=config.resume_id,
            type=InterviewType.TECHNICAL,
            difficulty_level=config.difficulty,
            status=InterviewStatus.SCHEDULED,
            mode=config.mode,
            configuration={
                "target_role": config.target_role,
                "focus_areas": config.focus_areas,
                "duration": config.duration,
                "resume_context": config.resume_context or ""
            }
        )

        db.add(session)
        await db.flush()

        r = await get_redis()
        session_data = {
            "id": str(session.id),
            "user_id": str(user_id),
            "status": InterviewState.INITIALIZED,
            "current_question_idx": 0,
            "config": json.dumps(config.dict()),
            "started_at": "",
            "questions": "[]"
        }
        await r.hset(f"interview:{session.id}", mapping=session_data)
        await r.expire(f"interview:{session.id}", 3600)

        return session

    async def get_session(self, session_id: UUID) -> Optional[Dict]:
        r = await get_redis()
        session_data = await r.hgetall(f"interview:{session_id}")
        if session_data:
            session_data["current_question_idx"] = int(session_data.get("current_question_idx", 0))
        return session_data

    async def update_session(self, session_id: UUID, updates: Dict) -> None:
        r = await get_redis()
        await r.hset(f"interview:{session_id}", mapping=updates)

    async def start_interview(self, session_id: UUID, db: AsyncSession) -> InterviewSession:
        result = await db.execute(select(InterviewSession).where(InterviewSession.id == session_id))
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(status_code=404, detail="Interview session not found")

        session.status = InterviewStatus.IN_PROGRESS
        session.started_at = datetime.utcnow()

        await self.update_session(session_id, {
            "status": InterviewState.IN_PROGRESS,
            "started_at": datetime.utcnow().isoformat()
        })

        questions = await self.generate_questions(session, db)

        question_dicts = []
        for q in questions:
            question_dicts.append({
                "id": str(q.id),
                "content": q.content,
                "type": q.question_type,
                "sequence_order": q.sequence_order,
            })

        await self.update_session(session_id, {
            "questions": json.dumps(question_dicts)
        })

        await db.commit()
        return session

    async def generate_questions(
        self,
        session: InterviewSession,
        db: AsyncSession
    ) -> List[InterviewQuestion]:
        """Generate AI-powered interview questions based on role, difficulty, and resume"""

        config = session.configuration
        target_role = config.get("target_role", "Software Engineer")
        difficulty = session.difficulty_level.value
        focus_areas = config.get("focus_areas") or ["system_design", "coding", "behavioral"]
        resume_context = config.get("resume_context", "")

        system_prompt = (
            "You are an expert technical interviewer. Generate realistic, challenging interview questions. "
            "Return ONLY a valid JSON object with no extra text."
        )

        resume_section = ""
        if resume_context:
            resume_section = f"\nCandidate resume/skills context:\n{resume_context[:2000]}\n"

        user_prompt = (
            f"Generate {len(focus_areas)} interview questions for a {target_role} role at {difficulty} difficulty.\n"
            f"Focus areas: {', '.join(focus_areas)}\n"
            f"{resume_section}"
            "Return JSON in this exact format:\n"
            '{"questions": [{"type": "coding", "content": "Question text here", "hints": ["hint1", "hint2"], "expected_points": ["point1", "point2"]}]}'
        )

        try:
            raw = await call_ai(system_prompt, user_prompt, json_mode=True)
            data = json.loads(raw)
            ai_questions = data.get("questions", [])
        except Exception:
            # Fallback to basic questions if AI fails
            ai_questions = self._fallback_questions(focus_areas, target_role)

        questions = []
        for i, q_data in enumerate(ai_questions[:len(focus_areas)]):
            question = InterviewQuestion(
                session_id=session.id,
                question_type=q_data.get("type", focus_areas[i % len(focus_areas)]),
                content=q_data.get("content", "Tell me about yourself."),
                expected_answer_points=q_data.get("expected_points", []),
                difficulty_level=self._difficulty_to_int(difficulty),
                sequence_order=i + 1,
                time_limit_seconds=300,
                hints=q_data.get("hints", [])
            )
            db.add(question)
            questions.append(question)

        await db.flush()
        return questions

    def _fallback_questions(self, focus_areas: List[str], role: str) -> List[Dict]:
        """Basic fallback questions if AI is unavailable"""
        templates = {
            "system_design": {"type": "system_design", "content": f"Design a scalable system for a {role} use case. Walk me through your architecture.", "hints": ["Think about scalability", "Consider data storage"], "expected_points": ["Components", "Scalability", "Trade-offs"]},
            "coding": {"type": "coding", "content": "Implement a function to find two numbers in an array that sum to a target value.", "hints": ["Consider a hash map", "Think about time complexity"], "expected_points": ["Correctness", "Complexity", "Edge cases"]},
            "behavioral": {"type": "behavioral", "content": "Tell me about a challenging project you worked on. What was your role and what did you learn?", "hints": ["Use STAR method", "Be specific"], "expected_points": ["Situation", "Action", "Result"]},
        }
        return [templates.get(area, templates["behavioral"]) for area in focus_areas]

    def _difficulty_to_int(self, difficulty: str) -> int:
        return {"easy": 3, "medium": 5, "hard": 8, "expert": 10}.get(difficulty, 5)

    async def process_answer(
        self,
        session_id: UUID,
        answer: AnswerSubmission,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Process candidate answer with AI analysis"""

        session_state = await self.get_session(session_id)
        if not session_state:
            raise HTTPException(status_code=404, detail="Session not found")

        result = await db.execute(
            select(InterviewQuestion).where(InterviewQuestion.id == answer.question_id)
        )
        question = result.scalar_one_or_none()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        response = InterviewResponse(
            question_id=answer.question_id,
            response_type="text" if answer.content else "code",
            content=answer.content,
            code_submission=answer.code_submission,
            language_used=answer.language_used,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            word_count=len(answer.content.split()) if answer.content else 0
        )
        db.add(response)
        await db.flush()

        analysis = await self.analyze_response(question, answer, db)

        response_analysis = ResponseAnalysis(
            response_id=response.id,
            technical_accuracy_score=analysis.get("technical_accuracy", 75.0),
            communication_score=analysis.get("communication", 80.0),
            problem_solving_score=analysis.get("problem_solving", 70.0),
            explanation_clarity_score=analysis.get("clarity", 75.0),
            confidence_score=analysis.get("confidence", 80.0),
            overall_score=analysis.get("overall", 75.0),
            strengths=analysis.get("strengths", []),
            weaknesses=analysis.get("weaknesses", []),
            improvement_suggestions=analysis.get("suggestions", {}),
            ai_model_version="openrouter-gpt4o-mini"
        )
        db.add(response_analysis)

        new_idx = session_state["current_question_idx"] + 1
        await self.update_session(session_id, {"current_question_idx": str(new_idx)})

        await db.commit()

        return {
            "response_id": str(response.id),
            "analysis": analysis,
            "next_question_idx": new_idx,
            "session_complete": new_idx >= len(json.loads(session_state.get("questions", "[]")))
        }

    async def analyze_response(
        self,
        question: InterviewQuestion,
        answer: AnswerSubmission,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """AI-powered response analysis"""

        candidate_answer = answer.content or answer.code_submission or ""

        if not candidate_answer.strip():
            return {
                "technical_accuracy": 0,
                "communication": 0,
                "problem_solving": 0,
                "clarity": 0,
                "confidence": 0,
                "overall": 0,
                "strengths": [],
                "weaknesses": ["No answer provided"],
                "suggestions": {},
                "ai_feedback": "No answer was provided for this question."
            }

        system_prompt = (
            "You are an expert technical interviewer evaluating a candidate's answer. "
            "Be fair but critical. Score honestly. Return ONLY valid JSON."
        )

        user_prompt = (
            f"Question: {question.content}\n\n"
            f"Expected points to cover: {', '.join(question.expected_answer_points or [])}\n\n"
            f"Candidate's answer:\n{candidate_answer[:3000]}\n\n"
            "Evaluate and return JSON in this exact format:\n"
            '{"technical_accuracy": 75, "communication": 80, "problem_solving": 70, "clarity": 75, "confidence": 80, '
            '"strengths": ["strength1", "strength2"], "weaknesses": ["weakness1"], '
            '"suggestions": {"improve": "suggestion here"}, "ai_feedback": "2-3 sentence overall feedback"}'
        )

        try:
            raw = await call_ai(system_prompt, user_prompt, json_mode=True)
            data = json.loads(raw)

            # Ensure all score fields are floats
            for field in ["technical_accuracy", "communication", "problem_solving", "clarity", "confidence"]:
                data[field] = float(data.get(field, 75))

            scores = [data["technical_accuracy"], data["communication"], data["problem_solving"]]
            data["overall"] = round(sum(scores) / len(scores), 1)

            return data

        except Exception:
            # Fallback to heuristic if AI fails
            word_count = len(candidate_answer.split())
            tech = min(100, 60 + (word_count // 10))
            comm = min(100, 70 + (candidate_answer.count(".") * 2))
            ps = min(100, 50 + (word_count // 15))
            return {
                "technical_accuracy": tech,
                "communication": comm,
                "problem_solving": ps,
                "clarity": comm,
                "confidence": 75.0,
                "overall": round((tech + comm + ps) / 3, 1),
                "strengths": ["Attempted the question"] if word_count > 20 else [],
                "weaknesses": ["Could not get AI analysis"] if word_count < 20 else [],
                "suggestions": {},
                "ai_feedback": "AI analysis unavailable. Score based on response length."
            }

    async def generate_feedback(
        self,
        session_id: UUID,
        db: AsyncSession
    ) -> FeedbackReport:
        """Generate final AI-powered feedback report"""

        result = await db.execute(
            select(InterviewResponse)
            .join(InterviewQuestion)
            .where(InterviewQuestion.session_id == session_id)
        )
        responses = result.scalars().all()

        if not responses:
            raise HTTPException(status_code=400, detail="No responses to analyze")

        total_technical = 0
        total_communication = 0
        total_problem_solving = 0
        all_strengths = []
        all_weaknesses = []
        all_feedback = []

        for response in responses:
            analysis_result = await db.execute(
                select(ResponseAnalysis).where(ResponseAnalysis.response_id == response.id)
            )
            analysis = analysis_result.scalar_one_or_none()
            if analysis:
                total_technical += analysis.technical_accuracy_score or 0
                total_communication += analysis.communication_score or 0
                total_problem_solving += analysis.problem_solving_score or 0
                all_strengths.extend(analysis.strengths or [])
                all_weaknesses.extend(analysis.weaknesses or [])

        count = len(responses)
        avg_technical = round(total_technical / count, 1)
        avg_communication = round(total_communication / count, 1)
        avg_problem_solving = round(total_problem_solving / count, 1)
        overall = round((avg_technical + avg_communication + avg_problem_solving) / 3, 1)

        # Generate AI recommendations
        recommendations = await self._ai_recommendations(
            avg_technical, avg_communication, avg_problem_solving,
            list(set(all_strengths)), list(set(all_weaknesses))
        )

        session_result = await db.execute(
            select(InterviewSession).where(InterviewSession.id == session_id)
        )
        session = session_result.scalar_one_or_none()
        if session:
            session.status = InterviewStatus.COMPLETED
            session.ended_at = datetime.utcnow()
            if session.started_at:
                session.duration_seconds = int((session.ended_at - session.started_at).total_seconds())

        await db.commit()

        return FeedbackReport(
            overall_score=overall,
            technical_accuracy=avg_technical,
            communication=avg_communication,
            problem_solving=avg_problem_solving,
            strengths=list(set(all_strengths))[:5],
            weaknesses=list(set(all_weaknesses))[:5],
            recommendations=recommendations,
            skill_assessments={
                "technical": avg_technical,
                "communication": avg_communication,
                "problem_solving": avg_problem_solving
            }
        )

    async def _ai_recommendations(
        self,
        technical: float,
        communication: float,
        problem_solving: float,
        strengths: List[str],
        weaknesses: List[str]
    ) -> List[str]:
        """Generate personalized AI recommendations"""

        system_prompt = "You are a career coach giving actionable interview improvement advice. Be specific and helpful."

        user_prompt = (
            f"Interview scores — Technical: {technical}/100, Communication: {communication}/100, Problem Solving: {problem_solving}/100\n"
            f"Strengths observed: {', '.join(strengths[:3]) or 'None noted'}\n"
            f"Weaknesses observed: {', '.join(weaknesses[:3]) or 'None noted'}\n\n"
            "Give 4 specific, actionable recommendations to improve future interview performance. "
            "Return as a JSON array: {\"recommendations\": [\"rec1\", \"rec2\", \"rec3\", \"rec4\"]}"
        )

        try:
            raw = await call_ai(system_prompt, user_prompt, json_mode=True)
            data = json.loads(raw)
            return data.get("recommendations", [])[:4]
        except Exception:
            recs = []
            if technical < 70:
                recs.append("Practice more data structures and algorithms on LeetCode")
            if communication < 70:
                recs.append("Structure answers using the STAR method")
            if problem_solving < 70:
                recs.append("Break down problems step by step before coding")
            recs.append("Do regular mock interviews to build confidence")
            return recs

# ==================== WebSocket Manager ====================

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, session_id: str, message: Dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

# ==================== FastAPI App ====================

app = FastAPI(title="Interview Service", version="2.0.0")
interview_manager = InterviewManager()
connection_manager = ConnectionManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_current_user_id() -> UUID:
    return uuid4()

@app.post("/v1/interviews", status_code=status.HTTP_201_CREATED)
async def create_interview(
    config: InterviewConfig,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    session = await interview_manager.create_session(user_id, config, db)
    return {"id": str(session.id), "status": session.status.value, "created_at": session.created_at.isoformat()}

@app.get("/v1/interviews/{session_id}")
async def get_interview(session_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(InterviewSession).where(InterviewSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")

    questions_result = await db.execute(
        select(InterviewQuestion).where(InterviewQuestion.session_id == session_id).order_by(InterviewQuestion.sequence_order)
    )
    questions = questions_result.scalars().all()

    return {
        "id": str(session.id),
        "user_id": str(session.user_id),
        "type": session.type.value,
        "difficulty": session.difficulty_level.value,
        "status": session.status.value,
        "mode": session.mode.value,
        "started_at": session.started_at.isoformat() if session.started_at else None,
        "ended_at": session.ended_at.isoformat() if session.ended_at else None,
        "duration_seconds": session.duration_seconds,
        "questions": [{"id": str(q.id), "type": q.question_type, "content": q.content, "sequence": q.sequence_order, "time_limit": q.time_limit_seconds} for q in questions]
    }

@app.post("/v1/interviews/{session_id}/start")
async def start_interview(session_id: UUID, db: AsyncSession = Depends(get_db)):
    session = await interview_manager.start_interview(session_id, db)
    question_result = await db.execute(
        select(InterviewQuestion).where(InterviewQuestion.session_id == session_id).order_by(InterviewQuestion.sequence_order).limit(1)
    )
    first_question = question_result.scalar_one_or_none()
    return {
        "session_id": str(session.id),
        "status": session.status.value,
        "question": {"id": str(first_question.id), "content": first_question.content, "type": first_question.question_type, "time_limit": first_question.time_limit_seconds, "hints": first_question.hints} if first_question else None
    }

@app.post("/v1/interviews/{session_id}/answer")
async def submit_answer(session_id: UUID, answer: AnswerSubmission, db: AsyncSession = Depends(get_db)):
    result = await interview_manager.process_answer(session_id, answer, db)
    next_q_result = await db.execute(
        select(InterviewQuestion).where(
            InterviewQuestion.session_id == session_id,
            InterviewQuestion.sequence_order == result["next_question_idx"] + 1
        )
    )
    next_question = next_q_result.scalar_one_or_none()
    return {
        "analysis": result["analysis"],
        "next_question": {"id": str(next_question.id), "content": next_question.content, "type": next_question.question_type, "sequence": next_question.sequence_order} if next_question else None,
        "complete": result["session_complete"]
    }

@app.post("/v1/interviews/{session_id}/hint")
async def request_hint(session_id: UUID, question_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(InterviewQuestion).where(InterviewQuestion.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    hints = question.hints or []
    return {"question_id": str(question_id), "hint": hints[0] if hints else "No hints available", "hint_level": 1}

@app.post("/v1/interviews/{session_id}/feedback")
async def generate_feedback(session_id: UUID, db: AsyncSession = Depends(get_db)):
    report = await interview_manager.generate_feedback(session_id, db)
    return {"session_id": str(session_id), "report": report.dict()}

@app.delete("/v1/interviews/{session_id}")
async def cancel_interview(session_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(InterviewSession).where(InterviewSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    session.status = InterviewStatus.CANCELLED
    await interview_manager.update_session(session_id, {"status": InterviewState.CANCELLED})
    await db.commit()
    return {"status": "cancelled"}

@app.websocket("/v1/interviews/{session_id}/stream")
async def interview_stream(websocket: WebSocket, session_id: UUID, token: str = Query(...)):
    await connection_manager.connect(str(session_id), websocket)
    try:
        await websocket.send_json({"type": "connected", "session_id": str(session_id)})
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
            elif msg_type == "answer":
                await websocket.send_json({"type": "answer_processed", "status": "analyzed"})
            elif msg_type == "request_hint":
                await websocket.send_json({"type": "hint", "content": "Think about the edge cases first."})
    except WebSocketDisconnect:
        connection_manager.disconnect(str(session_id))
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
        connection_manager.disconnect(str(session_id))

@app.get("/health")
async def health_check():
    ai_ok = bool(OPENROUTER_API_KEY and AsyncOpenAI is not None)
    return {"status": "healthy", "service": "interview", "ai_enabled": ai_ok}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)