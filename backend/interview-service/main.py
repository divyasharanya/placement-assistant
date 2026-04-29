# """
# Interview Service - Technical Interview Session Management
# FastAPI-based microservice for managing interview sessions with real-time WebSocket support
# """

# import os
# import json
# import asyncio
# from datetime import datetime
# from typing import Optional, List, Dict, Any
# from uuid import UUID, uuid4
# from enum import Enum

# from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, Query, status
# from fastapi.responses import JSONResponse
# from pydantic import BaseModel, Field
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
# from sqlalchemy import select, update
# import redis.asyncio as redis
# from starlette.datastructures import URL

# from database.models import (
#     InterviewSession, InterviewQuestion, InterviewResponse, ResponseAnalysis,
#     Resume, User, InterviewType, InterviewDifficulty, InterviewStatus, InterviewMode
# )

# # ==================== Configuration ====================

# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/aimock")
# REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
# AI_ENGINE_URL = os.getenv("AI_ENGINE_URL", "http://ai-engine:8003")

# # ==================== Database Setup ====================

# engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
# async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# async def get_db() -> AsyncSession:
#     async with async_session() as session:
#         try:
#             yield session
#             await session.commit()
#         except Exception:
#             await session.rollback()
#             raise

# # ==================== Redis Setup ====================

# redis_client: Optional[redis.Redis] = None

# async def get_redis() -> redis.Redis:
#     global redis_client
#     if redis_client is None:
#         redis_client = redis.from_url(REDIS_URL, decode_responses=True)
#     return redis_client

# # ==================== Pydantic Models ====================

# class InterviewConfig(BaseModel):
#     resume_id: Optional[UUID] = None
#     target_role: str = "Software Engineer"
#     difficulty: InterviewDifficulty = InterviewDifficulty.MEDIUM
#     mode: InterviewMode = InterviewMode.TEXT
#     focus_areas: Optional[List[str]] = None
#     duration: int = 30  # minutes

# class InterviewQuestionRequest(BaseModel):
#     session_id: UUID
#     question_type: str
#     content: str
#     difficulty_level: int = Field(ge=1, le=10)
#     sequence_order: int
#     time_limit_seconds: Optional[int] = None
#     hints: Optional[List[str]] = None

# class AnswerSubmission(BaseModel):
#     question_id: UUID
#     content: Optional[str] = None
#     audio_url: Optional[str] = None
#     code_submission: Optional[str] = None
#     language_used: Optional[str] = None

# class FeedbackReport(BaseModel):
#     overall_score: float
#     technical_accuracy: float
#     communication: float
#     problem_solving: float
#     strengths: List[str]
#     weaknesses: List[str]
#     recommendations: List[str]
#     skill_assessments: Dict[str, float]

# # ==================== Interview State Management ====================

# class InterviewState:
#     INITIALIZED = "initialized"
#     IN_PROGRESS = "in_progress"
#     PAUSED = "paused"
#     COMPLETED = "completed"
#     CANCELLED = "cancelled"

# class InterviewManager:
#     def __init__(self):
#         self.active_sessions: Dict[str, Dict] = {}
#         self.ai_engine_url = AI_ENGINE_URL
    
#     async def create_session(
#         self,
#         user_id: UUID,
#         config: InterviewConfig,
#         db: AsyncSession
#     ) -> InterviewSession:
#         """Initialize interview with context-aware question generation"""
        
#         # Create session record
#         session = InterviewSession(
#             user_id=user_id,
#             resume_id=config.resume_id,
#             type=InterviewType.TECHNICAL,
#             difficulty_level=config.difficulty,
#             status=InterviewStatus.SCHEDULED,
#             mode=config.mode,
#             configuration={
#                 "target_role": config.target_role,
#                 "focus_areas": config.focus_areas,
#                 "duration": config.duration
#             }
#         )
        
#         db.add(session)
#         await db.flush()
        
#         # Store in Redis for fast access
#         r = await get_redis()
#         session_data = {
#             "id": str(session.id),
#             "user_id": str(user_id),
#             "status": InterviewState.INITIALIZED,
#             "current_question_idx": 0,
#             "config": json.dumps(config.dict()),
#             "started_at": None,
#             "questions": "[]"
#         }
#         await r.hset(f"interview:{session.id}", mapping=session_data)
#         await r.expire(f"interview:{session.id}", 3600)  # 1 hour TTL
        
#         return session
    
#     async def get_session(self, session_id: UUID) -> Optional[Dict]:
#         """Get session from Redis"""
#         r = await get_redis()
#         session_data = await r.hgetall(f"interview:{session_id}")
#         if session_data:
#             session_data["current_question_idx"] = int(session_data.get("current_question_idx", 0))
#         return session_data
    
#     async def update_session(self, session_id: UUID, updates: Dict) -> None:
#         """Update session in Redis"""
#         r = await get_redis()
#         await r.hset(f"interview:{session_id}", mapping=updates)
    
#     async def start_interview(self, session_id: UUID, db: AsyncSession) -> InterviewSession:
#         """Mark interview as started and generate questions"""
        
#         # Get session from DB
#         result = await db.execute(select(InterviewSession).where(InterviewSession.id == session_id))
#         session = result.scalar_one_or_none()
        
#         if not session:
#             raise HTTPException(status_code=404, detail="Interview session not found")
        
#         session.status = InterviewStatus.IN_PROGRESS
#         session.started_at = datetime.utcnow()
        
#         # Update Redis
#         await self.update_session(session_id, {
#             "status": InterviewState.IN_PROGRESS,
#             "started_at": datetime.utcnow().isoformat()
#         })
        
#         # Generate questions (would call AI Engine in production)
#         questions = await self.generate_questions(session, db)
        
#         # Store questions
#         await self.update_session(session_id, {
#             "questions": json.dumps([q.dict() for q in questions])
#         })
        
#         await db.commit()
        
#         return session
    
#     async def generate_questions(
#         self,
#         session: InterviewSession,
#         db: AsyncSession
#     ) -> List[InterviewQuestion]:
#         """Generate interview questions based on configuration"""
        
#         # This would call the AI Engine in production
#         # For now, generate sample questions
#         focus_areas = session.configuration.get("focus_areas", ["system_design", "coding", "behavioral"])
#         difficulty = session.difficulty_level.value
        
#         question_templates = {
#             "system_design": [
#                 "Design a URL shortening service like bit.ly. What are the key components and how would you scale it?",
#                 "How would you design a real-time chat application? Consider scalability and reliability.",
#                 "Design a distributed cache system. How would you handle cache invalidation?",
#             ],
#             "coding": [
#                 "Implement a function to find the longest palindromic substring in a string.",
#                 "Write code to merge two sorted linked lists.",
#                 "Given an array of integers, find the maximum sum subarray.",
#             ],
#             "behavioral": [
#                 "Tell me about a challenging technical problem you solved. What was your approach?",
#                 "Describe a time when you had to work with a difficult team member.",
#                 "Tell me about a project you're most proud of. What was the impact?",
#             ]
#         }
        
#         questions = []
#         for i, area in enumerate(focus_areas):
#             templates = question_templates.get(area, question_templates["behavioral"])
#             content = templates[i % len(templates)]
            
#             question = InterviewQuestion(
#                 session_id=session.id,
#                 question_type=area,
#                 content=content,
#                 expected_answer_points=self._get_expected_points(area),
#                 difficulty_level=self._get_difficulty_level(difficulty),
#                 sequence_order=i + 1,
#                 time_limit_seconds=300,  # 5 minutes
#                 hints=self._get_hints(area)
#             )
            
#             db.add(question)
#             questions.append(question)
        
#         await db.flush()
        
#         return questions
    
#     def _get_expected_points(self, question_type: str) -> List[str]:
#         """Get expected answer points for a question type"""
        
#         points = {
#             "system_design": [
#                 "Identify key components (API, storage, caching)",
#                 "Discuss scalability considerations",
#                 "Address reliability and fault tolerance"
#             ],
#             "coding": [
#                 "Correctness of the algorithm",
#                 "Time and space complexity analysis",
#                 "Edge case handling"
#             ],
#             "behavioral": [
#                 "Specific example with context",
#                 "Actions taken",
#                 "Results and impact"
#             ]
#         }
        
#         return points.get(question_type, points["behavioral"])
    
#     def _get_difficulty_level(self, difficulty: str) -> int:
#         """Convert difficulty to numeric level"""
#         levels = {
#             "easy": 3,
#             "medium": 5,
#             "hard": 8,
#             "expert": 10
#         }
#         return levels.get(difficulty, 5)
    
#     def _get_hints(self, question_type: str) -> List[str]:
#         """Get hints for question type"""
        
#         hints = {
#             "system_design": [
#                 "Think about the data flow and storage requirements first",
#                 "Consider using diagrams to visualize the architecture",
#                 "Don't forget to discuss trade-offs"
#             ],
#             "coding": [
#                 "Try brute force first, then optimize",
#                 "Consider using a hash map for O(1) lookups",
#                 "Think about edge cases like empty input"
#             ],
#             "behavioral": [
#                 "Use the STAR method (Situation, Task, Action, Result)",
#                 "Be specific and quantify your impact",
#                 "Focus on what you learned"
#             ]
#         }
        
#         return hints.get(question_type, hints["behavioral"])
    
#     async def process_answer(
#         self,
#         session_id: UUID,
#         answer: AnswerSubmission,
#         db: AsyncSession
#     ) -> Dict[str, Any]:
#         """Process candidate answer and generate analysis"""
        
#         # Get session state
#         session_state = await self.get_session(session_id)
        
#         if not session_state:
#             raise HTTPException(status_code=404, detail="Session not found")
        
#         # Get question
#         result = await db.execute(
#             select(InterviewQuestion).where(InterviewQuestion.id == answer.question_id)
#         )
#         question = result.scalar_one_or_none()
        
#         if not question:
#             raise HTTPException(status_code=404, detail="Question not found")
        
#         # Create response record
#         response = InterviewResponse(
#             question_id=answer.question_id,
#             response_type="text" if answer.content else "code",
#             content=answer.content,
#             code_submission=answer.code_submission,
#             language_used=answer.language_used,
#             start_time=datetime.utcnow(),
#             end_time=datetime.utcnow(),
#             word_count=len(answer.content.split()) if answer.content else 0
#         )
        
#         db.add(response)
#         await db.flush()
        
#         # Analyze response (would call AI Engine in production)
#         analysis = await self.analyze_response(question, answer, db)
        
#         # Create analysis record
#         response_analysis = ResponseAnalysis(
#             response_id=response.id,
#             technical_accuracy_score=analysis.get("technical_accuracy", 75.0),
#             communication_score=analysis.get("communication", 80.0),
#             problem_solving_score=analysis.get("problem_solving", 70.0),
#             explanation_clarity_score=analysis.get("clarity", 75.0),
#             confidence_score=analysis.get("confidence", 80.0),
#             overall_score=analysis.get("overall", 75.0),
#             strengths=analysis.get("strengths", []),
#             weaknesses=analysis.get("weaknesses", []),
#             improvement_suggestions=analysis.get("suggestions", {}),
#             ai_model_version="v1.0"
#         )
        
#         db.add(response_analysis)
        
#         # Update session progress
#         new_idx = session_state["current_question_idx"] + 1
#         await self.update_session(session_id, {"current_question_idx": new_idx})
        
#         await db.commit()
        
#         return {
#             "response_id": str(response.id),
#             "analysis": analysis,
#             "next_question_idx": new_idx,
#             "session_complete": new_idx >= len(json.loads(session_state.get("questions", "[]")))
#         }
    
#     async def analyze_response(
#         self,
#         question: InterviewQuestion,
#         answer: AnswerSubmission,
#         db: AsyncSession
#     ) -> Dict[str, Any]:
#         """Analyze response using AI"""
        
#         # This would call the AI Engine service in production
#         # For now, return mock analysis based on content length
        
#         content = answer.content or answer.code_submission or ""
        
#         # Simple heuristic analysis
#         word_count = len(content.split())
        
#         # Score based on response length and structure
#         technical_score = min(100, 60 + (word_count // 10))
#         communication_score = min(100, 70 + (content.count(".") * 2))
#         problem_solving_score = min(100, 50 + (word_count // 15))
        
#         strengths = []
#         weaknesses = []
#         suggestions = {}
        
#         if word_count > 50:
#             strengths.append("Provided a detailed response")
#         else:
#             weaknesses.append("Response could be more detailed")
        
#         if content.count(".") > 3:
#             strengths.append("Well-structured explanation")
        
#         if answer.code_submission:
#             if "def " in answer.code_submission or "function " in answer.code_submission:
#                 strengths.append("Included code implementation")
#             else:
#                 weaknesses.append("Missing code implementation")
        
#         return {
#             "technical_accuracy": technical_score,
#             "communication": communication_score,
#             "problem_solving": problem_solving_score,
#             "clarity": communication_score,
#             "confidence": 75.0,
#             "overall": (technical_score + communication_score + problem_solving_score) / 3,
#             "strengths": strengths,
#             "weaknesses": weaknesses,
#             "suggestions": suggestions
#         }
    
#     async def generate_feedback(
#         self,
#         session_id: UUID,
#         db: AsyncSession
#     ) -> FeedbackReport:
#         """Generate final feedback report"""
        
#         # Get all responses for the session
#         result = await db.execute(
#             select(InterviewResponse)
#             .join(InterviewQuestion)
#             .where(InterviewQuestion.session_id == session_id)
#         )
#         responses = result.scalars().all()
        
#         if not responses:
#             raise HTTPException(status_code=400, detail="No responses to analyze")
        
#         # Calculate aggregate scores
#         total_technical = 0
#         total_communication = 0
#         total_problem_solving = 0
#         all_strengths = []
#         all_weaknesses = []
        
#         for response in responses:
#             analysis_result = await db.execute(
#                 select(ResponseAnalysis).where(ResponseAnalysis.response_id == response.id)
#             )
#             analysis = analysis_result.scalar_one_or_none()
            
#             if analysis:
#                 total_technical += analysis.technical_accuracy_score or 0
#                 total_communication += analysis.communication_score or 0
#                 total_problem_solving += analysis.problem_solving_score or 0
#                 all_strengths.extend(analysis.strengths or [])
#                 all_weaknesses.extend(analysis.weaknesses or [])
        
#         count = len(responses)
#         avg_technical = total_technical / count
#         avg_communication = total_communication / count
#         avg_problem_solving = total_problem_solving / count
#         overall = (avg_technical + avg_communication + avg_problem_solving) / 3
        
#         # Update session as completed
#         session_result = await db.execute(
#             select(InterviewSession).where(InterviewSession.id == session_id)
#         )
#         session = session_result.scalar_one_or_none()
        
#         if session:
#             session.status = InterviewStatus.COMPLETED
#             session.ended_at = datetime.utcnow()
#             session.duration_seconds = int((session.ended_at - session.started_at).total_seconds())
        
#         await db.commit()
        
#         return FeedbackReport(
#             overall_score=round(overall, 1),
#             technical_accuracy=round(avg_technical, 1),
#             communication=round(avg_communication, 1),
#             problem_solving=round(avg_problem_solving, 1),
#             strengths=list(set(all_strengths))[:5],
#             weaknesses=list(set(all_weaknesses))[:5],
#             recommendations=self._generate_recommendations(avg_technical, avg_communication, avg_problem_solving),
#             skill_assessments={
#                 "technical": round(avg_technical, 1),
#                 "communication": round(avg_communication, 1),
#                 "problem_solving": round(avg_problem_solving, 1)
#             }
#         )
    
#     def _generate_recommendations(
#         self,
#         technical: float,
#         communication: float,
#         problem_solving: float
#     ) -> List[str]:
#         """Generate improvement recommendations"""
        
#         recommendations = []
        
#         if technical < 70:
#             recommendations.append("Focus on deeper understanding of core concepts and data structures")
#         if communication < 70:
#             recommendations.append("Practice structuring your answers with clear examples and explanations")
#         if problem_solving < 70:
#             recommendations.append("Work on breaking down problems into smaller, manageable steps")
        
#         recommendations.append("Practice system design questions regularly")
#         recommendations.append("Consider mock interviews to build confidence")
        
#         return recommendations

# # ==================== WebSocket Manager ====================

# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: Dict[str, WebSocket] = {}
    
#     async def connect(self, session_id: str, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections[session_id] = websocket
    
#     def disconnect(self, session_id: str):
#         if session_id in self.active_connections:
#             del self.active_connections[session_id]
    
#     async def send_message(self, session_id: str, message: Dict):
#         if session_id in self.active_connections:
#             await self.active_connections[session_id].send_json(message)
    
#     async def broadcast(self, message: Dict):
#         for connection in self.active_connections.values():
#             await connection.send_json(message)

# # ==================== FastAPI App ====================

# app = FastAPI(title="Interview Service", version="1.0.0")
# interview_manager = InterviewManager()
# connection_manager = ConnectionManager()

# async def get_current_user_id() -> UUID:
#     """In production, extract from JWT token"""
#     return uuid4()

# @app.post("/v1/interviews", status_code=status.HTTP_201_CREATED)
# async def create_interview(
#     config: InterviewConfig,
#     db: AsyncSession = Depends(get_db),
#     user_id: UUID = Depends(get_current_user_id)
# ):
#     """Schedule a new interview session"""
    
#     session = await interview_manager.create_session(user_id, config, db)
    
#     return {
#         "id": str(session.id),
#         "status": session.status.value,
#         "created_at": session.created_at.isoformat()
#     }

# @app.get("/v1/interviews/{session_id}")
# async def get_interview(
#     session_id: UUID,
#     db: AsyncSession = Depends(get_db)
# ):
#     """Get interview details"""
    
#     result = await db.execute(select(InterviewSession).where(InterviewSession.id == session_id))
#     session = result.scalar_one_or_none()
    
#     if not session:
#         raise HTTPException(status_code=404, detail="Interview not found")
    
#     # Get questions
#     questions_result = await db.execute(
#         select(InterviewQuestion)
#         .where(InterviewQuestion.session_id == session_id)
#         .order_by(InterviewQuestion.sequence_order)
#     )
#     questions = questions_result.scalars().all()
    
#     return {
#         "id": str(session.id),
#         "user_id": str(session.user_id),
#         "type": session.type.value,
#         "difficulty": session.difficulty_level.value,
#         "status": session.status.value,
#         "mode": session.mode.value,
#         "started_at": session.started_at.isoformat() if session.started_at else None,
#         "ended_at": session.ended_at.isoformat() if session.ended_at else None,
#         "duration_seconds": session.duration_seconds,
#         "questions": [
#             {
#                 "id": str(q.id),
#                 "type": q.question_type,
#                 "content": q.content,
#                 "sequence": q.sequence_order,
#                 "time_limit": q.time_limit_seconds
#             }
#             for q in questions
#         ]
#     }

# @app.post("/v1/interviews/{session_id}/start")
# async def start_interview(
#     session_id: UUID,
#     db: AsyncSession = Depends(get_db)
# ):
#     """Start the interview and get first question"""
    
#     session = await interview_manager.start_interview(session_id, db)
    
#     # Get first question
#     question_result = await db.execute(
#         select(InterviewQuestion)
#         .where(InterviewQuestion.session_id == session_id)
#         .order_by(InterviewQuestion.sequence_order)
#         .limit(1)
#     )
#     first_question = question_result.scalar_one_or_none()
    
#     return {
#         "session_id": str(session.id),
#         "status": session.status.value,
#         "question": {
#             "id": str(first_question.id),
#             "content": first_question.content,
#             "type": first_question.question_type,
#             "time_limit": first_question.time_limit_seconds,
#             "hints": first_question.hints
#         } if first_question else None
#     }

# @app.post("/v1/interviews/{session_id}/answer")
# async def submit_answer(
#     session_id: UUID,
#     answer: AnswerSubmission,
#     db: AsyncSession = Depends(get_db)
# ):
#     """Submit an answer to a question"""
    
#     result = await interview_manager.process_answer(session_id, answer, db)
    
#     # Get next question if available
#     next_q_result = await db.execute(
#         select(InterviewQuestion)
#         .where(
#             InterviewQuestion.session_id == session_id,
#             InterviewQuestion.sequence_order == result["next_question_idx"] + 1
#         )
#     )
#     next_question = next_q_result.scalar_one_or_none()
    
#     return {
#         "analysis": result["analysis"],
#         "next_question": {
#             "id": str(next_question.id),
#             "content": next_question.content,
#             "type": next_question.question_type,
#             "sequence": next_question.sequence_order
#         } if next_question else None,
#         "complete": result["session_complete"]
#     }

# @app.post("/v1/interviews/{session_id}/hint")
# async def request_hint(
#     session_id: UUID,
#     question_id: UUID,
#     db: AsyncSession = Depends(get_db)
# ):
#     """Get a hint for the current question"""
    
#     result = await db.execute(select(InterviewQuestion).where(InterviewQuestion.id == question_id))
#     question = result.scalar_one_or_none()
    
#     if not question:
#         raise HTTPException(status_code=404, detail="Question not found")
    
#     hints = question.hints or []
    
#     return {
#         "question_id": str(question_id),
#         "hint": hints[0] if hints else "No hints available",
#         "hint_level": 1
#     }

# @app.post("/v1/interviews/{session_id}/feedback")
# async def generate_feedback(
#     session_id: UUID,
#     db: AsyncSession = Depends(get_db)
# ):
#     """Generate final feedback report"""
    
#     report = await interview_manager.generate_feedback(session_id, db)
    
#     return {
#         "session_id": str(session_id),
#         "report": report.dict()
#     }

# @app.delete("/v1/interviews/{session_id}")
# async def cancel_interview(
#     session_id: UUID,
#     db: AsyncSession = Depends(get_db)
# ):
#     """Cancel an interview session"""
    
#     result = await db.execute(select(InterviewSession).where(InterviewSession.id == session_id))
#     session = result.scalar_one_or_none()
    
#     if not session:
#         raise HTTPException(status_code=404, detail="Interview not found")
    
#     session.status = InterviewStatus.CANCELLED
    
#     # Update Redis
#     await interview_manager.update_session(session_id, {"status": InterviewState.CANCELLED})
    
#     await db.commit()
    
#     return {"status": "cancelled"}

# # ==================== WebSocket Endpoint ====================

# @app.websocket("/v1/interviews/{session_id}/stream")
# async def interview_stream(
#     websocket: WebSocket,
#     session_id: UUID,
#     token: str = Query(...)
# ):
#     """WebSocket endpoint for real-time interview"""
    
#     await connection_manager.connect(str(session_id), websocket)
    
#     try:
#         # Send welcome message
#         await websocket.send_json({
#             "type": "connected",
#             "session_id": str(session_id)
#         })
        
#         # Handle messages
#         while True:
#             data = await websocket.receive_json()
#             msg_type = data.get("type")
            
#             if msg_type == "ping":
#                 await websocket.send_json({"type": "pong"})
            
#             elif msg_type == "answer":
#                 # Process answer
#                 answer = AnswerSubmission(
#                     question_id=UUID(data["question_id"]),
#                     content=data.get("content"),
#                     code_submission=data.get("code")
#                 )
#                 # Process and send result
#                 await websocket.send_json({
#                     "type": "answer_processed",
#                     "status": "analyzed"
#                 })
            
#             elif msg_type == "request_hint":
#                 await websocket.send_json({
#                     "type": "hint",
#                     "content": "Think about the edge cases first."
#                 })
    
#     except WebSocketDisconnect:
#         connection_manager.disconnect(str(session_id))
    
#     except Exception as e:
#         await websocket.send_json({
#             "type": "error",
#             "message": str(e)
#         })
#         connection_manager.disconnect(str(session_id))

# @app.get("/health")
# async def health_check():
#     return {"status": "healthy", "service": "interview"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8003)








#the trial cde maannnnnnnnnnnnnnnnnnnn
"""
Interview Service - Technical Interview Session Management
FastAPI-based microservice for managing interview sessions with real-time WebSocket support
Upgraded with OpenRouter AI for real question generation and response analysis
"""

# import os
# import json
# import asyncio
# from datetime import datetime
# from typing import Optional, List, Dict, Any
# from uuid import UUID, uuid4
# from enum import Enum
# from pathlib import Path

# from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, Query, status
# from fastapi.responses import JSONResponse
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
# from sqlalchemy import select, update
# import redis.asyncio as redis

# try:
#     from openai import AsyncOpenAI
# except ImportError:
#     AsyncOpenAI = None

# from database.models import (
#     InterviewSession, InterviewQuestion, InterviewResponse, ResponseAnalysis,
#     Resume, User, InterviewType, InterviewDifficulty, InterviewStatus, InterviewMode
# )

# # ==================== Configuration ====================

# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/aimock")
# REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
# AI_ENGINE_URL = os.getenv("AI_ENGINE_URL", "http://ai-engine:8003")

# # Read OpenRouter API key from file
# _api_key_path = Path(r"D:\placement_assisstant\backend\resume-service\api.txt")
# if _api_key_path.exists():
#     with open(_api_key_path, "r") as f:
#         OPENROUTER_API_KEY = f.read().strip()
# else:
#     OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
# AI_MODEL = "openai/gpt-4o-mini"  # cheap and fast via OpenRouter

# # ==================== Database Setup ====================

# engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
# async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# async def get_db() -> AsyncSession:
#     async with async_session() as session:
#         try:
#             yield session
#             await session.commit()
#         except Exception:
#             await session.rollback()
#             raise

# # ==================== Redis Setup ====================

# redis_client: Optional[redis.Redis] = None

# async def get_redis() -> redis.Redis:
#     global redis_client
#     if redis_client is None:
#         redis_client = redis.from_url(REDIS_URL, decode_responses=True)
#     return redis_client

# # ==================== AI Client ====================

# def get_ai_client() -> Optional[Any]:
#     """Get OpenRouter AI client"""
#     if not OPENROUTER_API_KEY or AsyncOpenAI is None:
#         return None
#     return AsyncOpenAI(
#         api_key=OPENROUTER_API_KEY,
#         base_url=OPENROUTER_BASE_URL
#     )

# async def call_ai(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
#     """Call OpenRouter AI and return response text"""
#     client = get_ai_client()
#     if not client:
#         raise HTTPException(status_code=503, detail="AI service not configured. Check OPENROUTER_API_KEY.")

#     kwargs = {
#         "model": AI_MODEL,
#         "messages": [
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt},
#         ],
#         "temperature": 0.7,
#         "max_tokens": 1500,
#     }
#     if json_mode:
#         kwargs["response_format"] = {"type": "json_object"}
#         kwargs["temperature"] = 0

#     try:
#         completion = await client.chat.completions.create(**kwargs)
#         return completion.choices[0].message.content or ""
#     except Exception as e:
#         raise HTTPException(status_code=502, detail=f"AI call failed: {str(e)}")

# # ==================== Pydantic Models ====================

# class InterviewConfig(BaseModel):
#     resume_id: Optional[UUID] = None
#     target_role: str = "Software Engineer"
#     difficulty: InterviewDifficulty = InterviewDifficulty.MEDIUM
#     mode: InterviewMode = InterviewMode.TEXT
#     focus_areas: Optional[List[str]] = None
#     duration: int = 30  # minutes
#     resume_context: Optional[str] = None  # parsed resume text/skills for AI context

# class InterviewQuestionRequest(BaseModel):
#     session_id: UUID
#     question_type: str
#     content: str
#     difficulty_level: int = Field(ge=1, le=10)
#     sequence_order: int
#     time_limit_seconds: Optional[int] = None
#     hints: Optional[List[str]] = None

# class AnswerSubmission(BaseModel):
#     question_id: UUID
#     content: Optional[str] = None
#     audio_url: Optional[str] = None
#     code_submission: Optional[str] = None
#     language_used: Optional[str] = None

# class FeedbackReport(BaseModel):
#     overall_score: float
#     technical_accuracy: float
#     communication: float
#     problem_solving: float
#     strengths: List[str]
#     weaknesses: List[str]
#     recommendations: List[str]
#     skill_assessments: Dict[str, float]

# # ==================== Interview State Management ====================

# class InterviewState:
#     INITIALIZED = "initialized"
#     IN_PROGRESS = "in_progress"
#     PAUSED = "paused"
#     COMPLETED = "completed"
#     CANCELLED = "cancelled"

# # ==================== Interview Manager ====================

# class InterviewManager:
#     def __init__(self):
#         self.active_sessions: Dict[str, Dict] = {}

#     async def create_session(
#         self,
#         user_id: UUID,
#         config: InterviewConfig,
#         db: AsyncSession
#     ) -> InterviewSession:
#         """Initialize interview session"""

#         session = InterviewSession(
#             user_id=user_id,
#             resume_id=config.resume_id,
#             type=InterviewType.TECHNICAL,
#             difficulty_level=config.difficulty,
#             status=InterviewStatus.SCHEDULED,
#             mode=config.mode,
#             configuration={
#                 "target_role": config.target_role,
#                 "focus_areas": config.focus_areas,
#                 "duration": config.duration,
#                 "resume_context": config.resume_context or ""
#             }
#         )

#         db.add(session)
#         await db.flush()

#         r = await get_redis()
#         session_data = {
#             "id": str(session.id),
#             "user_id": str(user_id),
#             "status": InterviewState.INITIALIZED,
#             "current_question_idx": 0,
#             "config": json.dumps(config.dict()),
#             "started_at": "",
#             "questions": "[]"
#         }
#         await r.hset(f"interview:{session.id}", mapping=session_data)
#         await r.expire(f"interview:{session.id}", 3600)

#         return session

#     async def get_session(self, session_id: UUID) -> Optional[Dict]:
#         r = await get_redis()
#         session_data = await r.hgetall(f"interview:{session_id}")
#         if session_data:
#             session_data["current_question_idx"] = int(session_data.get("current_question_idx", 0))
#         return session_data

#     async def update_session(self, session_id: UUID, updates: Dict) -> None:
#         r = await get_redis()
#         await r.hset(f"interview:{session_id}", mapping=updates)

#     async def start_interview(self, session_id: UUID, db: AsyncSession) -> InterviewSession:
#         result = await db.execute(select(InterviewSession).where(InterviewSession.id == session_id))
#         session = result.scalar_one_or_none()

#         if not session:
#             raise HTTPException(status_code=404, detail="Interview session not found")

#         session.status = InterviewStatus.IN_PROGRESS
#         session.started_at = datetime.utcnow()

#         await self.update_session(session_id, {
#             "status": InterviewState.IN_PROGRESS,
#             "started_at": datetime.utcnow().isoformat()
#         })

#         questions = await self.generate_questions(session, db)

#         question_dicts = []
#         for q in questions:
#             question_dicts.append({
#                 "id": str(q.id),
#                 "content": q.content,
#                 "type": q.question_type,
#                 "sequence_order": q.sequence_order,
#             })

#         await self.update_session(session_id, {
#             "questions": json.dumps(question_dicts)
#         })

#         await db.commit()
#         return session

#     async def generate_questions(
#         self,
#         session: InterviewSession,
#         db: AsyncSession
#     ) -> List[InterviewQuestion]:
#         """Generate AI-powered interview questions based on role, difficulty, and resume"""

#         config = session.configuration
#         target_role = config.get("target_role", "Software Engineer")
#         difficulty = session.difficulty_level.value
#         focus_areas = config.get("focus_areas") or ["system_design", "coding", "behavioral"]
#         resume_context = config.get("resume_context", "")

#         system_prompt = (
#             "You are an expert technical interviewer. Generate realistic, challenging interview questions. "
#             "Return ONLY a valid JSON object with no extra text."
#         )

#         resume_section = ""
#         if resume_context:
#             resume_section = f"\nCandidate resume/skills context:\n{resume_context[:2000]}\n"

#         user_prompt = (
#             f"Generate {len(focus_areas)} interview questions for a {target_role} role at {difficulty} difficulty.\n"
#             f"Focus areas: {', '.join(focus_areas)}\n"
#             f"{resume_section}"
#             "Return JSON in this exact format:\n"
#             '{"questions": [{"type": "coding", "content": "Question text here", "hints": ["hint1", "hint2"], "expected_points": ["point1", "point2"]}]}'
#         )

#         try:
#             raw = await call_ai(system_prompt, user_prompt, json_mode=True)
#             data = json.loads(raw)
#             ai_questions = data.get("questions", [])
#         except Exception:
#             # Fallback to basic questions if AI fails
#             ai_questions = self._fallback_questions(focus_areas, target_role)

#         questions = []
#         for i, q_data in enumerate(ai_questions[:len(focus_areas)]):
#             question = InterviewQuestion(
#                 session_id=session.id,
#                 question_type=q_data.get("type", focus_areas[i % len(focus_areas)]),
#                 content=q_data.get("content", "Tell me about yourself."),
#                 expected_answer_points=q_data.get("expected_points", []),
#                 difficulty_level=self._difficulty_to_int(difficulty),
#                 sequence_order=i + 1,
#                 time_limit_seconds=300,
#                 hints=q_data.get("hints", [])
#             )
#             db.add(question)
#             questions.append(question)

#         await db.flush()
#         return questions

#     def _fallback_questions(self, focus_areas: List[str], role: str) -> List[Dict]:
#         """Basic fallback questions if AI is unavailable"""
#         templates = {
#             "system_design": {"type": "system_design", "content": f"Design a scalable system for a {role} use case. Walk me through your architecture.", "hints": ["Think about scalability", "Consider data storage"], "expected_points": ["Components", "Scalability", "Trade-offs"]},
#             "coding": {"type": "coding", "content": "Implement a function to find two numbers in an array that sum to a target value.", "hints": ["Consider a hash map", "Think about time complexity"], "expected_points": ["Correctness", "Complexity", "Edge cases"]},
#             "behavioral": {"type": "behavioral", "content": "Tell me about a challenging project you worked on. What was your role and what did you learn?", "hints": ["Use STAR method", "Be specific"], "expected_points": ["Situation", "Action", "Result"]},
#         }
#         return [templates.get(area, templates["behavioral"]) for area in focus_areas]

#     def _difficulty_to_int(self, difficulty: str) -> int:
#         return {"easy": 3, "medium": 5, "hard": 8, "expert": 10}.get(difficulty, 5)

#     async def process_answer(
#         self,
#         session_id: UUID,
#         answer: AnswerSubmission,
#         db: AsyncSession
#     ) -> Dict[str, Any]:
#         """Process candidate answer with AI analysis"""

#         session_state = await self.get_session(session_id)
#         if not session_state:
#             raise HTTPException(status_code=404, detail="Session not found")

#         result = await db.execute(
#             select(InterviewQuestion).where(InterviewQuestion.id == answer.question_id)
#         )
#         question = result.scalar_one_or_none()
#         if not question:
#             raise HTTPException(status_code=404, detail="Question not found")

#         response = InterviewResponse(
#             question_id=answer.question_id,
#             response_type="text" if answer.content else "code",
#             content=answer.content,
#             code_submission=answer.code_submission,
#             language_used=answer.language_used,
#             start_time=datetime.utcnow(),
#             end_time=datetime.utcnow(),
#             word_count=len(answer.content.split()) if answer.content else 0
#         )
#         db.add(response)
#         await db.flush()

#         analysis = await self.analyze_response(question, answer, db)

#         response_analysis = ResponseAnalysis(
#             response_id=response.id,
#             technical_accuracy_score=analysis.get("technical_accuracy", 75.0),
#             communication_score=analysis.get("communication", 80.0),
#             problem_solving_score=analysis.get("problem_solving", 70.0),
#             explanation_clarity_score=analysis.get("clarity", 75.0),
#             confidence_score=analysis.get("confidence", 80.0),
#             overall_score=analysis.get("overall", 75.0),
#             strengths=analysis.get("strengths", []),
#             weaknesses=analysis.get("weaknesses", []),
#             improvement_suggestions=analysis.get("suggestions", {}),
#             ai_model_version="openrouter-gpt4o-mini"
#         )
#         db.add(response_analysis)

#         new_idx = session_state["current_question_idx"] + 1
#         await self.update_session(session_id, {"current_question_idx": str(new_idx)})

#         await db.commit()

#         return {
#             "response_id": str(response.id),
#             "analysis": analysis,
#             "next_question_idx": new_idx,
#             "session_complete": new_idx >= len(json.loads(session_state.get("questions", "[]")))
#         }

#     async def analyze_response(
#         self,
#         question: InterviewQuestion,
#         answer: AnswerSubmission,
#         db: AsyncSession
#     ) -> Dict[str, Any]:
#         """AI-powered response analysis"""

#         candidate_answer = answer.content or answer.code_submission or ""

#         if not candidate_answer.strip():
#             return {
#                 "technical_accuracy": 0,
#                 "communication": 0,
#                 "problem_solving": 0,
#                 "clarity": 0,
#                 "confidence": 0,
#                 "overall": 0,
#                 "strengths": [],
#                 "weaknesses": ["No answer provided"],
#                 "suggestions": {},
#                 "ai_feedback": "No answer was provided for this question."
#             }

#         system_prompt = (
#             "You are an expert technical interviewer evaluating a candidate's answer. "
#             "Be fair but critical. Score honestly. Return ONLY valid JSON."
#         )

#         user_prompt = (
#             f"Question: {question.content}\n\n"
#             f"Expected points to cover: {', '.join(question.expected_answer_points or [])}\n\n"
#             f"Candidate's answer:\n{candidate_answer[:3000]}\n\n"
#             "Evaluate and return JSON in this exact format:\n"
#             '{"technical_accuracy": 75, "communication": 80, "problem_solving": 70, "clarity": 75, "confidence": 80, '
#             '"strengths": ["strength1", "strength2"], "weaknesses": ["weakness1"], '
#             '"suggestions": {"improve": "suggestion here"}, "ai_feedback": "2-3 sentence overall feedback"}'
#         )

#         try:
#             raw = await call_ai(system_prompt, user_prompt, json_mode=True)
#             data = json.loads(raw)

#             # Ensure all score fields are floats
#             for field in ["technical_accuracy", "communication", "problem_solving", "clarity", "confidence"]:
#                 data[field] = float(data.get(field, 75))

#             scores = [data["technical_accuracy"], data["communication"], data["problem_solving"]]
#             data["overall"] = round(sum(scores) / len(scores), 1)

#             return data

#         except Exception:
#             # Fallback to heuristic if AI fails
#             word_count = len(candidate_answer.split())
#             tech = min(100, 60 + (word_count // 10))
#             comm = min(100, 70 + (candidate_answer.count(".") * 2))
#             ps = min(100, 50 + (word_count // 15))
#             return {
#                 "technical_accuracy": tech,
#                 "communication": comm,
#                 "problem_solving": ps,
#                 "clarity": comm,
#                 "confidence": 75.0,
#                 "overall": round((tech + comm + ps) / 3, 1),
#                 "strengths": ["Attempted the question"] if word_count > 20 else [],
#                 "weaknesses": ["Could not get AI analysis"] if word_count < 20 else [],
#                 "suggestions": {},
#                 "ai_feedback": "AI analysis unavailable. Score based on response length."
#             }

#     async def generate_feedback(
#         self,
#         session_id: UUID,
#         db: AsyncSession
#     ) -> FeedbackReport:
#         """Generate final AI-powered feedback report"""

#         result = await db.execute(
#             select(InterviewResponse)
#             .join(InterviewQuestion)
#             .where(InterviewQuestion.session_id == session_id)
#         )
#         responses = result.scalars().all()

#         if not responses:
#             raise HTTPException(status_code=400, detail="No responses to analyze")

#         total_technical = 0
#         total_communication = 0
#         total_problem_solving = 0
#         all_strengths = []
#         all_weaknesses = []
#         all_feedback = []

#         for response in responses:
#             analysis_result = await db.execute(
#                 select(ResponseAnalysis).where(ResponseAnalysis.response_id == response.id)
#             )
#             analysis = analysis_result.scalar_one_or_none()
#             if analysis:
#                 total_technical += analysis.technical_accuracy_score or 0
#                 total_communication += analysis.communication_score or 0
#                 total_problem_solving += analysis.problem_solving_score or 0
#                 all_strengths.extend(analysis.strengths or [])
#                 all_weaknesses.extend(analysis.weaknesses or [])

#         count = len(responses)
#         avg_technical = round(total_technical / count, 1)
#         avg_communication = round(total_communication / count, 1)
#         avg_problem_solving = round(total_problem_solving / count, 1)
#         overall = round((avg_technical + avg_communication + avg_problem_solving) / 3, 1)

#         # Generate AI recommendations
#         recommendations = await self._ai_recommendations(
#             avg_technical, avg_communication, avg_problem_solving,
#             list(set(all_strengths)), list(set(all_weaknesses))
#         )

#         session_result = await db.execute(
#             select(InterviewSession).where(InterviewSession.id == session_id)
#         )
#         session = session_result.scalar_one_or_none()
#         if session:
#             session.status = InterviewStatus.COMPLETED
#             session.ended_at = datetime.utcnow()
#             if session.started_at:
#                 session.duration_seconds = int((session.ended_at - session.started_at).total_seconds())

#         await db.commit()

#         return FeedbackReport(
#             overall_score=overall,
#             technical_accuracy=avg_technical,
#             communication=avg_communication,
#             problem_solving=avg_problem_solving,
#             strengths=list(set(all_strengths))[:5],
#             weaknesses=list(set(all_weaknesses))[:5],
#             recommendations=recommendations,
#             skill_assessments={
#                 "technical": avg_technical,
#                 "communication": avg_communication,
#                 "problem_solving": avg_problem_solving
#             }
#         )

#     async def _ai_recommendations(
#         self,
#         technical: float,
#         communication: float,
#         problem_solving: float,
#         strengths: List[str],
#         weaknesses: List[str]
#     ) -> List[str]:
#         """Generate personalized AI recommendations"""

#         system_prompt = "You are a career coach giving actionable interview improvement advice. Be specific and helpful."

#         user_prompt = (
#             f"Interview scores — Technical: {technical}/100, Communication: {communication}/100, Problem Solving: {problem_solving}/100\n"
#             f"Strengths observed: {', '.join(strengths[:3]) or 'None noted'}\n"
#             f"Weaknesses observed: {', '.join(weaknesses[:3]) or 'None noted'}\n\n"
#             "Give 4 specific, actionable recommendations to improve future interview performance. "
#             "Return as a JSON array: {\"recommendations\": [\"rec1\", \"rec2\", \"rec3\", \"rec4\"]}"
#         )

#         try:
#             raw = await call_ai(system_prompt, user_prompt, json_mode=True)
#             data = json.loads(raw)
#             return data.get("recommendations", [])[:4]
#         except Exception:
#             recs = []
#             if technical < 70:
#                 recs.append("Practice more data structures and algorithms on LeetCode")
#             if communication < 70:
#                 recs.append("Structure answers using the STAR method")
#             if problem_solving < 70:
#                 recs.append("Break down problems step by step before coding")
#             recs.append("Do regular mock interviews to build confidence")
#             return recs

# # ==================== WebSocket Manager ====================

# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: Dict[str, WebSocket] = {}

#     async def connect(self, session_id: str, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections[session_id] = websocket

#     def disconnect(self, session_id: str):
#         if session_id in self.active_connections:
#             del self.active_connections[session_id]

#     async def send_message(self, session_id: str, message: Dict):
#         if session_id in self.active_connections:
#             await self.active_connections[session_id].send_json(message)

# # ==================== FastAPI App ====================

# app = FastAPI(title="Interview Service", version="2.0.0")
# interview_manager = InterviewManager()
# connection_manager = ConnectionManager()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
#     allow_credentials=False,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# async def get_current_user_id() -> UUID:
#     return uuid4()

# @app.post("/v1/interviews", status_code=status.HTTP_201_CREATED)
# async def create_interview(
#     config: InterviewConfig,
#     db: AsyncSession = Depends(get_db),
#     user_id: UUID = Depends(get_current_user_id)
# ):
#     session = await interview_manager.create_session(user_id, config, db)
#     return {"id": str(session.id), "status": session.status.value, "created_at": session.created_at.isoformat()}

# @app.get("/v1/interviews/{session_id}")
# async def get_interview(session_id: UUID, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(InterviewSession).where(InterviewSession.id == session_id))
#     session = result.scalar_one_or_none()
#     if not session:
#         raise HTTPException(status_code=404, detail="Interview not found")

#     questions_result = await db.execute(
#         select(InterviewQuestion).where(InterviewQuestion.session_id == session_id).order_by(InterviewQuestion.sequence_order)
#     )
#     questions = questions_result.scalars().all()

#     return {
#         "id": str(session.id),
#         "user_id": str(session.user_id),
#         "type": session.type.value,
#         "difficulty": session.difficulty_level.value,
#         "status": session.status.value,
#         "mode": session.mode.value,
#         "started_at": session.started_at.isoformat() if session.started_at else None,
#         "ended_at": session.ended_at.isoformat() if session.ended_at else None,
#         "duration_seconds": session.duration_seconds,
#         "questions": [{"id": str(q.id), "type": q.question_type, "content": q.content, "sequence": q.sequence_order, "time_limit": q.time_limit_seconds} for q in questions]
#     }

# @app.post("/v1/interviews/{session_id}/start")
# async def start_interview(session_id: UUID, db: AsyncSession = Depends(get_db)):
#     session = await interview_manager.start_interview(session_id, db)
#     question_result = await db.execute(
#         select(InterviewQuestion).where(InterviewQuestion.session_id == session_id).order_by(InterviewQuestion.sequence_order).limit(1)
#     )
#     first_question = question_result.scalar_one_or_none()
#     return {
#         "session_id": str(session.id),
#         "status": session.status.value,
#         "question": {"id": str(first_question.id), "content": first_question.content, "type": first_question.question_type, "time_limit": first_question.time_limit_seconds, "hints": first_question.hints} if first_question else None
#     }

# @app.post("/v1/interviews/{session_id}/answer")
# async def submit_answer(session_id: UUID, answer: AnswerSubmission, db: AsyncSession = Depends(get_db)):
#     result = await interview_manager.process_answer(session_id, answer, db)
#     next_q_result = await db.execute(
#         select(InterviewQuestion).where(
#             InterviewQuestion.session_id == session_id,
#             InterviewQuestion.sequence_order == result["next_question_idx"] + 1
#         )
#     )
#     next_question = next_q_result.scalar_one_or_none()
#     return {
#         "analysis": result["analysis"],
#         "next_question": {"id": str(next_question.id), "content": next_question.content, "type": next_question.question_type, "sequence": next_question.sequence_order} if next_question else None,
#         "complete": result["session_complete"]
#     }

# @app.post("/v1/interviews/{session_id}/hint")
# async def request_hint(session_id: UUID, question_id: UUID, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(InterviewQuestion).where(InterviewQuestion.id == question_id))
#     question = result.scalar_one_or_none()
#     if not question:
#         raise HTTPException(status_code=404, detail="Question not found")
#     hints = question.hints or []
#     return {"question_id": str(question_id), "hint": hints[0] if hints else "No hints available", "hint_level": 1}

# @app.post("/v1/interviews/{session_id}/feedback")
# async def generate_feedback(session_id: UUID, db: AsyncSession = Depends(get_db)):
#     report = await interview_manager.generate_feedback(session_id, db)
#     return {"session_id": str(session_id), "report": report.dict()}

# @app.delete("/v1/interviews/{session_id}")
# async def cancel_interview(session_id: UUID, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(InterviewSession).where(InterviewSession.id == session_id))
#     session = result.scalar_one_or_none()
#     if not session:
#         raise HTTPException(status_code=404, detail="Interview not found")
#     session.status = InterviewStatus.CANCELLED
#     await interview_manager.update_session(session_id, {"status": InterviewState.CANCELLED})
#     await db.commit()
#     return {"status": "cancelled"}

# @app.websocket("/v1/interviews/{session_id}/stream")
# async def interview_stream(websocket: WebSocket, session_id: UUID, token: str = Query(...)):
#     await connection_manager.connect(str(session_id), websocket)
#     try:
#         await websocket.send_json({"type": "connected", "session_id": str(session_id)})
#         while True:
#             data = await websocket.receive_json()
#             msg_type = data.get("type")
#             if msg_type == "ping":
#                 await websocket.send_json({"type": "pong"})
#             elif msg_type == "answer":
#                 await websocket.send_json({"type": "answer_processed", "status": "analyzed"})
#             elif msg_type == "request_hint":
#                 await websocket.send_json({"type": "hint", "content": "Think about the edge cases first."})
#     except WebSocketDisconnect:
#         connection_manager.disconnect(str(session_id))
#     except Exception as e:
#         await websocket.send_json({"type": "error", "message": str(e)})
#         connection_manager.disconnect(str(session_id))

# @app.get("/health")
# async def health_check():
#     ai_ok = bool(OPENROUTER_API_KEY and AsyncOpenAI is not None)
#     return {"status": "healthy", "service": "interview", "ai_enabled": ai_ok}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8003)




"""
Interview Service - main.py
Run: python main.py
Requires: pip install fastapi uvicorn openai pydantic
Port: 8000
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

# ============================================================
#  CONFIGURATION
# ============================================================

_api_key_path = Path(r"D:\placement_assisstant\backend\resume-service\api.txt")
if _api_key_path.exists():
    with open(_api_key_path, "r") as f:
        OPENROUTER_API_KEY = f.read().strip()
else:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
AI_MODEL = "openai/gpt-4o-mini"

# In-memory store — replace with Redis/DB in production
SESSIONS: Dict[str, Dict] = {}

# ============================================================
#  AI CLIENT
# ============================================================

def get_ai_client():
    if not OPENROUTER_API_KEY or AsyncOpenAI is None:
        return None
    return AsyncOpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)


async def call_ai(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    client = get_ai_client()
    if not client:
        raise HTTPException(503, "AI not configured. Set OPENROUTER_API_KEY.")
    kwargs: Dict[str, Any] = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 2000,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
        kwargs["temperature"] = 0
    try:
        resp = await client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content or ""
    except Exception as e:
        raise HTTPException(502, f"AI call failed: {e}")

# ============================================================
#  DOMAIN / STAGE METADATA
# ============================================================

DOMAINS = [
    {"id": "backend",      "label": "Backend Engineering",         "icon": "⚙️"},
    {"id": "frontend",     "label": "Frontend Development",        "icon": "🎨"},
    {"id": "fullstack",    "label": "Full Stack Development",      "icon": "🔗"},
    {"id": "data_science", "label": "Data Science & ML",           "icon": "📊"},
    {"id": "devops",       "label": "DevOps & Cloud",              "icon": "☁️"},
    {"id": "system_design","label": "System Design",               "icon": "🏗️"},
    {"id": "mobile",       "label": "Mobile Development",          "icon": "📱"},
    {"id": "security",     "label": "Cybersecurity",               "icon": "🔒"},
    {"id": "database",     "label": "Database Engineering",        "icon": "🗄️"},
    {"id": "general_swe",  "label": "General Software Engineering","icon": "💻"},
    {"id": "product",      "label": "Product Management",          "icon": "📋"},
    {"id": "behavioral",   "label": "Behavioral / HR Round",       "icon": "🤝"},
    {"id": "dsa",          "label": "DSA & Algorithms",            "icon": "🧮"},
]

STAGE_LABELS = {
    "introduction": "Introduction",
    "technical":    "Technical Round",
    "behavioral":   "Behavioral Round",
    "system_design":"System Design",
    "closing":      "Closing",
}

def _get_stage(question_index: int, total: int) -> str:
    pct = question_index / max(total - 1, 1)
    if pct == 0:       return "introduction"
    if pct < 0.35:     return "technical"
    if pct < 0.70:     return "behavioral"
    if pct < 0.90:     return "system_design"
    return "closing"

# ============================================================
#  QUESTION GENERATOR
# ============================================================

async def generate_questions(
    domain: str,
    difficulty: str,
    num_questions: int,
    resume_text: Optional[str],
    focus_areas: Optional[List[str]],
) -> List[Dict]:

    resume_section = (
        f"\nCandidate resume (use this to personalise at least 40% of questions):\n{resume_text[:3000]}\n"
        if resume_text and resume_text.strip()
        else f"No resume provided — generate standard {domain} questions."
    )
    focus_section = (
        f"Extra focus areas: {', '.join(focus_areas)}" if focus_areas else ""
    )

    system_prompt = (
        "You are a senior technical interviewer at a top-tier tech company. "
        "Generate realistic, challenging questions. "
        "If a resume is given, ask specifically about projects and technologies in it. "
        "Return ONLY valid JSON — no markdown, no extra text."
    )
    user_prompt = f"""
Generate exactly {num_questions} interview questions for a {domain} role at {difficulty} difficulty.
{resume_section}
{focus_section}

Return this exact JSON:
{{
  "questions": [
    {{
      "type": "technical|behavioral|resume_specific|system_design|coding|introduction|closing",
      "content": "Full question text",
      "follow_ups": ["follow-up 1"],
      "expected_points": ["key point 1", "key point 2"],
      "time_limit_seconds": 120
    }}
  ]
}}

First question should always be a friendly introduction ("Tell me about yourself...").
Last question should be a closing ("Do you have any questions for us?").
"""
    try:
        raw  = await call_ai(system_prompt, user_prompt, json_mode=True)
        data = json.loads(raw)
        qs   = data.get("questions", [])
        while len(qs) < num_questions:
            qs.append(_fallback_q(domain, len(qs)))
        return qs[:num_questions]
    except Exception:
        return [_fallback_q(domain, i) for i in range(num_questions)]


def _fallback_q(domain: str, idx: int) -> Dict:
    pool = [
        {"type":"introduction",  "content":"Tell me about yourself and your background.",
         "follow_ups":[],"expected_points":["Clear intro","Relevant experience"],"time_limit_seconds":90},
        {"type":"technical",     "content":f"What are the most important concepts in {domain} you rely on?",
         "follow_ups":["Example?"],"expected_points":["Depth","Practical use"],"time_limit_seconds":120},
        {"type":"behavioral",    "content":"Describe a time you solved a hard technical problem.",
         "follow_ups":["What did you learn?"],"expected_points":["Situation","Action","Result"],"time_limit_seconds":120},
        {"type":"system_design", "content":f"Design a scalable system relevant to {domain}.",
         "follow_ups":["How would you scale it?"],"expected_points":["Components","Scale","Trade-offs"],"time_limit_seconds":180},
        {"type":"closing",       "content":"Do you have any questions for us?",
         "follow_ups":[],"expected_points":["Curiosity","Engagement"],"time_limit_seconds":60},
    ]
    return pool[idx % len(pool)]

# ============================================================
#  ANSWER ANALYSER
# ============================================================

async def analyze_answer(question: Dict, answer_text: str, domain: str) -> Dict:
    if not answer_text or len(answer_text.strip()) < 5:
        return {
            "score": 0,
            "technical_accuracy": 0, "communication": 0, "problem_solving": 0,
            "strengths": [], "improvements": ["No answer provided"],
            "ai_feedback": "No answer was provided.",
            "key_points_covered": [], "key_points_missed": question.get("expected_points", []),
        }

    system_prompt = (
        "You are an expert technical interviewer scoring a candidate's answer. "
        "Be fair, specific, constructive. Score out of 100. Return ONLY valid JSON."
    )
    user_prompt = f"""
Domain: {domain}
Question type: {question.get('type','general')}
Question: {question.get('content','')}
Expected key points: {', '.join(question.get('expected_points', []))}

Candidate's answer:
{answer_text[:2000]}

Return exactly this JSON (no extra keys):
{{
  "technical_accuracy": <0-100>,
  "communication": <0-100>,
  "problem_solving": <0-100>,
  "strengths": ["strength 1", "strength 2"],
  "improvements": ["area 1"],
  "ai_feedback": "2-3 sentence constructive feedback",
  "key_points_covered": ["point"],
  "key_points_missed": ["point"]
}}
"""
    try:
        raw  = await call_ai(system_prompt, user_prompt, json_mode=True)
        data = json.loads(raw)
        for f in ["technical_accuracy", "communication", "problem_solving"]:
            data[f] = float(data.get(f, 60))
        data["score"] = round(
            (data["technical_accuracy"] + data["communication"] + data["problem_solving"]) / 3, 1
        )
        # normalise key names expected by frontend
        if "weaknesses" in data and "improvements" not in data:
            data["improvements"] = data.pop("weaknesses")
        return data
    except Exception:
        words = len(answer_text.split())
        sc = min(100, 50 + words // 5)
        return {
            "score": float(sc),
            "technical_accuracy": sc, "communication": sc, "problem_solving": sc,
            "strengths":    ["Attempted the question"] if words > 15 else [],
            "improvements": ["Answer was too brief"]   if words < 15 else [],
            "ai_feedback":  "AI analysis unavailable — score based on answer length.",
            "key_points_covered": [],
            "key_points_missed":  question.get("expected_points", []),
        }

# ============================================================
#  FINAL REPORT GENERATOR
# ============================================================

async def generate_final_report(session: Dict) -> Dict:
    analyses  = session.get("analyses", [])
    questions = session.get("questions", [])
    if not analyses:
        raise HTTPException(400, "No answers to analyse.")

    count     = len(analyses)
    avg_tech  = round(sum(a.get("technical_accuracy", 0) for a in analyses) / count, 1)
    avg_comm  = round(sum(a.get("communication",       0) for a in analyses) / count, 1)
    avg_ps    = round(sum(a.get("problem_solving",     0) for a in analyses) / count, 1)
    overall   = round((avg_tech + avg_comm + avg_ps) / 3, 1)

    all_strengths    = []
    all_improvements = []
    for a in analyses:
        all_strengths.extend(a.get("strengths",    []))
        all_improvements.extend(a.get("improvements", []))

    # AI recommendations
    system_prompt = "You are a career coach. Give specific, actionable interview improvement advice. Return ONLY JSON."
    user_prompt   = f"""
Interview summary — Domain: {session.get('domain','SWE')}
Technical: {avg_tech}/100  Communication: {avg_comm}/100  Problem Solving: {avg_ps}/100
Strengths:    {', '.join(list(set(all_strengths))[:3])    or 'none noted'}
Improvements: {', '.join(list(set(all_improvements))[:3]) or 'none noted'}

Give 4 specific recommendations.
Return: {{"suggestions": ["rec1","rec2","rec3","rec4"]}}
"""
    try:
        raw  = await call_ai(system_prompt, user_prompt, json_mode=True)
        sugg = json.loads(raw).get("suggestions", [])[:4]
    except Exception:
        sugg = []
        if avg_tech < 70: sugg.append("Practice core technical concepts with hands-on projects.")
        if avg_comm < 70: sugg.append("Structure answers using STAR (Situation, Task, Action, Result).")
        if avg_ps   < 70: sugg.append("Think out loud when problem-solving — process matters.")
        sugg.append("Do regular mock interviews to build comfort and confidence.")

    per_question = [
        {
            "question_number": i + 1,
            "question":  q.get("content", ""),
            "type":      q.get("type",    "general"),
            "score":     round(a.get("score", 0), 1),
            "feedback":  a.get("ai_feedback", ""),
            "strengths": a.get("strengths",    []),
            "improvements": a.get("improvements", []),
            "points_covered": a.get("key_points_covered", []),
            "points_missed":  a.get("key_points_missed",  []),
        }
        for i, (q, a) in enumerate(zip(questions, analyses))
    ]

    grade = "A" if overall >= 85 else "B" if overall >= 70 else "C" if overall >= 55 else "D"

    return {
        "overall_score":      overall,
        "communication_score": avg_comm,
        "technical_score":    avg_tech,
        "problem_solving":    avg_ps,
        "total_questions":    count,
        "strengths":          list(set(all_strengths))[:5],
        "improvements":       list(set(all_improvements))[:5],
        "suggestions":        sugg,
        "category_scores":    {"technical": avg_tech, "communication": avg_comm, "problem_solving": avg_ps},
        "per_question":       per_question,
        "grade":              grade,
    }

# ============================================================
#  PYDANTIC MODELS  (match frontend fetch payloads exactly)
# ============================================================

class StartInterviewRequest(BaseModel):
    user_id:      Optional[str]       = None
    domain:       Optional[str]       = "General Software Engineering"
    difficulty:   str                  = "medium"
    num_questions: int                 = Field(default=5, ge=2, le=10)
    resume_text:  Optional[str]       = None
    focus_areas:  Optional[List[str]] = None   # frontend legacy field (ignored if domain set)

class AnswerRequest(BaseModel):
    session_id:  str
    user_answer: str            # frontend sends "user_answer"
    question_id: Optional[int] = None  # frontend sends 1-based question number

class EndInterviewRequest(BaseModel):
    session_id: str

# ============================================================
#  FASTAPI APP
# ============================================================

app = FastAPI(title="Interview Service", version="4.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── GET /api/domains ─────────────────────────────────────────
@app.get("/api/domains")
async def get_domains():
    return {"domains": DOMAINS}

# ── POST /api/start-interview ────────────────────────────────
@app.post("/api/start-interview")
async def start_interview(req: StartInterviewRequest):
    """
    Frontend calls: POST /api/start-interview
    Payload: { user_id, domain, difficulty, num_questions, resume_text, focus_areas }
    Returns: { session_id, question, question_number, stage, stage_label, total_questions }
    """
    session_id = str(uuid4())

    # Resolve domain: if frontend sent legacy focus_areas without domain, map it
    domain = req.domain or "General Software Engineering"

    questions = await generate_questions(
        domain        = domain,
        difficulty    = req.difficulty,
        num_questions = req.num_questions,
        resume_text   = req.resume_text,
        focus_areas   = req.focus_areas,
    )

    SESSIONS[session_id] = {
        "session_id":   session_id,
        "user_id":      req.user_id,
        "domain":       domain,
        "difficulty":   req.difficulty,
        "questions":    questions,
        "answers":      [],
        "analyses":     [],
        "current_index": 0,
        "status":       "in_progress",
        "has_resume":   bool(req.resume_text and req.resume_text.strip()),
        "started_at":   datetime.utcnow().isoformat(),
        "completed_at": None,
    }

    first_q = questions[0]
    stage   = _get_stage(0, len(questions))

    return {
        "session_id":     session_id,
        "question":       first_q["content"],        # frontend reads `data.question`
        "next_question":  first_q["content"],        # fallback alias
        "question_number": 1,
        "total_questions": len(questions),
        "stage":          stage,
        "stage_label":    STAGE_LABELS.get(stage, "Interview"),
        "question_type":  first_q.get("type", "introduction"),
        "time_limit_seconds": first_q.get("time_limit_seconds", 90),
        "domain":         domain,
        "difficulty":     req.difficulty,
        "has_resume":     bool(req.resume_text and req.resume_text.strip()),
    }

# ── POST /api/answer ─────────────────────────────────────────
@app.post("/api/answer")
async def submit_answer(req: AnswerRequest):
    """
    Frontend calls: POST /api/answer
    Payload: { session_id, user_answer, question_id }
    Returns: {
        analysis: { score, strengths, improvements, ai_feedback },
        next_question,
        question_number,
        current_stage,
        stage_label,
        interview_completed,
        final_score   (only when interview_completed=true)
    }
    """
    session = SESSIONS.get(req.session_id)
    if not session:
        raise HTTPException(404, "Session not found.")
    if session["status"] != "in_progress":
        raise HTTPException(400, "Interview is not in progress.")

    idx       = session["current_index"]
    questions = session["questions"]

    if idx >= len(questions):
        raise HTTPException(400, "All questions already answered.")

    question     = questions[idx]
    answer_text  = req.user_answer.strip()

    # AI analysis
    analysis = await analyze_answer(question, answer_text, session["domain"])

    session["answers"].append({
        "question_index": idx,
        "answer_text":    answer_text,
        "submitted_at":   datetime.utcnow().isoformat(),
    })
    session["analyses"].append(analysis)
    session["current_index"] = idx + 1

    next_idx     = idx + 1
    is_complete  = next_idx >= len(questions)

    if is_complete:
        session["status"]       = "completed"
        session["completed_at"] = datetime.utcnow().isoformat()

    # Build response
    response: Dict[str, Any] = {
        "analysis": {
            "score":        round(analysis.get("score", 0), 1),
            "strengths":    analysis.get("strengths",    []),
            "improvements": analysis.get("improvements", []),
            "ai_feedback":  analysis.get("ai_feedback",  ""),
            "technical_accuracy": analysis.get("technical_accuracy", 0),
            "communication":      analysis.get("communication",      0),
            "problem_solving":    analysis.get("problem_solving",    0),
        },
        "interview_completed": is_complete,
        "questions_answered":  next_idx,
        "total_questions":     len(questions),
    }

    if is_complete:
        # Compute quick final score inline (full report via /api/end-interview)
        analyses  = session["analyses"]
        avg_score = round(sum(a.get("score", 0) for a in analyses) / len(analyses), 1)
        response["final_score"] = avg_score
    else:
        nq    = questions[next_idx]
        stage = _get_stage(next_idx, len(questions))
        response["next_question"]  = nq["content"]
        response["question_number"] = next_idx + 1
        response["current_stage"]  = stage
        response["stage_label"]    = STAGE_LABELS.get(stage, "Interview")
        response["question_type"]  = nq.get("type", "technical")
        response["time_limit_seconds"] = nq.get("time_limit_seconds", 120)

    return response

# ── POST /api/end-interview ──────────────────────────────────
@app.post("/api/end-interview")
async def end_interview(req: EndInterviewRequest):
    """
    Frontend calls: POST /api/end-interview
    Payload: { session_id }
    Returns: { evaluation: { overall_score, communication_score, technical_score,
                              total_questions, strengths, improvements, suggestions,
                              category_scores, per_question, grade } }
    """
    session = SESSIONS.get(req.session_id)
    if not session:
        raise HTTPException(404, "Session not found.")

    # Force completion if called early
    if session["status"] == "in_progress":
        session["status"]       = "completed"
        session["completed_at"] = datetime.utcnow().isoformat()

    if not session["analyses"]:
        raise HTTPException(400, "No answers submitted yet.")

    evaluation = await generate_final_report(session)

    return {
        "session_id":   req.session_id,
        "evaluation":   evaluation,
        "domain":       session["domain"],
        "difficulty":   session["difficulty"],
        "has_resume":   session["has_resume"],
        "started_at":   session["started_at"],
        "completed_at": session["completed_at"],
    }

# ── GET /api/session/{session_id} ────────────────────────────
@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found.")
    return {
        "session_id":        session_id,
        "status":            session["status"],
        "current_index":     session["current_index"],
        "total_questions":   len(session["questions"]),
        "questions_answered": len(session["analyses"]),
        "domain":            session["domain"],
        "difficulty":        session["difficulty"],
    }

# ── GET /api/domains ─────────────────────────────────────────
@app.get("/api/domains")
async def list_domains():
    return {"domains": DOMAINS}

# ── WebSocket /api/ws/{session_id} ───────────────────────────
class WSManager:
    def __init__(self):
        self._conns: Dict[str, WebSocket] = {}

    async def connect(self, sid: str, ws: WebSocket):
        await ws.accept()
        self._conns[sid] = ws

    def disconnect(self, sid: str):
        self._conns.pop(sid, None)

    async def send(self, sid: str, data: Dict):
        ws = self._conns.get(sid)
        if ws:
            await ws.send_json(data)

ws_mgr = WSManager()

@app.websocket("/api/ws/{session_id}")
async def interview_ws(websocket: WebSocket, session_id: str):
    await ws_mgr.connect(session_id, websocket)
    try:
        await ws_mgr.send(session_id, {"type": "connected"})
        while True:
            data     = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "ping":
                await ws_mgr.send(session_id, {"type": "pong"})

            elif msg_type == "submit_answer":
                session = SESSIONS.get(session_id)
                if not session:
                    await ws_mgr.send(session_id, {"type": "error", "message": "Session not found"})
                    continue

                answer_text = data.get("user_answer") or data.get("answer_text", "")
                await ws_mgr.send(session_id, {"type": "analyzing"})

                idx      = session["current_index"]
                questions = session["questions"]
                if idx < len(questions):
                    analysis = await analyze_answer(questions[idx], answer_text, session["domain"])
                    session["answers"].append({"question_index": idx, "answer_text": answer_text})
                    session["analyses"].append(analysis)
                    session["current_index"] = idx + 1

                    next_idx    = idx + 1
                    is_complete = next_idx >= len(questions)
                    if is_complete:
                        session["status"] = "completed"

                    next_q = None
                    if not is_complete:
                        nq     = questions[next_idx]
                        stage  = _get_stage(next_idx, len(questions))
                        next_q = {
                            "index":   next_idx,
                            "number":  next_idx + 1,
                            "content": nq["content"],
                            "type":    nq["type"],
                            "stage":   stage,
                            "stage_label": STAGE_LABELS.get(stage, "Interview"),
                        }

                    await ws_mgr.send(session_id, {
                        "type":         "answer_analyzed",
                        "analysis":     {"score": analysis.get("score", 0), "ai_feedback": analysis.get("ai_feedback", ""), "strengths": analysis.get("strengths", []), "improvements": analysis.get("improvements", [])},
                        "next_question": next_q,
                        "is_complete":  is_complete,
                    })

            elif msg_type == "get_report":
                session = SESSIONS.get(session_id)
                if session and session["analyses"]:
                    report = await generate_final_report(session)
                    await ws_mgr.send(session_id, {"type": "final_report", "report": report})

    except WebSocketDisconnect:
        ws_mgr.disconnect(session_id)
    except Exception as e:
        try:
            await ws_mgr.send(session_id, {"type": "error", "message": str(e)})
        except Exception:
            pass
        ws_mgr.disconnect(session_id)

# ── Health check ─────────────────────────────────────────────
@app.get("/health")
async def health():
    return {
        "status":          "healthy",
        "service":         "interview-v4",
        "ai_enabled":      bool(OPENROUTER_API_KEY and AsyncOpenAI is not None),
        "active_sessions": len(SESSIONS),
    }

# ── Entry point ───────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)