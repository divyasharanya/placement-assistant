"""
AI Engine - Multi-Agent AI Architecture
FastAPI-based microservice for AI-powered interview features
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from enum import Enum
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import redis.asyncio as redis
import httpx

# ==================== Configuration ====================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# ==================== Redis Setup ====================

redis_client: Optional[redis.Redis] = None

async def get_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    return redis_client

# ==================== Pydantic Models ====================

class AgentRole(str, Enum):
    INTERVIEWER = "interviewer"
    EVALUATOR = "evaluator"
    COACH = "coach"
    ATS_ANALYZER = "ats_analyzer"
    CODE_REVIEWER = "code_reviewer"

@dataclass
class AIContext:
    user_profile: Dict[str, Any]
    resume_data: Dict[str, Any]
    session_history: List[Dict]
    current_difficulty: int
    emotional_state: Optional[str] = None

class InterviewPlanRequest(BaseModel):
    target_role: str
    experience_level: str
    difficulty: str
    focus_areas: List[str]
    duration_minutes: int
    resume_data: Optional[Dict[str, Any]] = None

class QuestionGenerateRequest(BaseModel):
    topic: str
    difficulty: int
    context: Optional[Dict[str, Any]] = None
    question_number: int = 1

class ResponseAnalysisRequest(BaseModel):
    question: str
    question_type: str
    expected_points: List[str]
    answer: str
    mode: str = "text"

class FollowUpRequest(BaseModel):
    original_question: str
    answer: str
    analysis: Dict[str, Any]
    depth_level: int

class FeedbackRequest(BaseModel):
    session_responses: List[Dict[str, Any]]
    user_profile: Optional[Dict[str, Any]] = None

# ==================== Prompt Templates ====================

SYSTEM_PROMPTS = {
    "interviewer": """You are an expert technical interviewer at a top-tier tech company (Google, Meta, Amazon, etc.).
You conduct technical interviews that are challenging but fair.
Your goal is to assess the candidate's problem-solving abilities, technical depth, and communication skills.

Guidelines:
- Ask clear, unambiguous questions
- Start with the candidate's experience level in mind
- Probe deeper when needed to understand their thought process
- Provide hints when they get stuck (without giving away the answer)
- Be professional and encouraging

Assessment Criteria:
1. Technical Accuracy - Is their understanding correct?
2. Problem Solving - How do they approach problems?
3. Communication - Can they explain complex concepts clearly?
4. Depth - Do they understand the "why" behind things?
""",

    "evaluator": """You are a strict but fair technical evaluator.
Your job is to assess interview responses objectively and provide constructive feedback.

Evaluation Framework:
1. Technical Correctness (0-100): Are facts accurate?
2. Completeness (0-100): Did they cover all key aspects?
3. Depth (0-100): Do they understand underlying concepts?
4. Communication (0-100): Is their explanation clear?
5. Problem Solving (0-100): How do they approach challenges?

Provide specific, actionable feedback that helps the candidate improve.
""",

    "coach": """You are an AI career coach specializing in technical interview preparation.
Help candidates understand their strengths, weaknesses, and areas for improvement.

Your role:
- Provide encouraging, supportive feedback
- Suggest specific study resources
- Help them develop a learning plan
- Build their confidence while being honest about gaps
""",

    "code_reviewer": """You are a senior software engineer conducting a code review.
Evaluate code for correctness, efficiency, readability, and best practices.

Assessment Areas:
1. Correctness - Does it solve the problem?
2. Efficiency - Time and space complexity
3. Code Quality - Naming, structure, readability
4. Edge Cases - Handling boundary conditions
5. Best Practices - Language idioms, patterns
"""
}

RESPONSE_EVALUATOR_PROMPT = """
Evaluate this technical interview response rigorously.

Question: {question}
Question Type: {question_type}
Expected Key Points: {expected_points}

Candidate's Answer:
{answer}

Evaluate on:
1. Technical Accuracy (0-100): Are the technical facts accurate?
2. Completeness (0-100): Did they cover all key aspects?
3. Depth (0-100): Did they demonstrate deep understanding?
4. Communication Clarity (0-100): Is their explanation clear?
5. Problem Solving (0-100): How do they approach problems?

Provide specific feedback:
- What they got right (be specific)
- What they missed (critical gaps)
- Misconceptions (if any)
- Suggested improvements

Return JSON format:
{{
    "scores": {{
        "technical_accuracy": number,
        "completeness": number,
        "depth": number,
        "communication": number,
        "problem_solving": number,
        "overall": number
    }},
    "strengths": ["specific strength 1", "strength 2"],
    "weaknesses": ["specific gap 1", "gap 2"],
    "suggestions": ["improvement 1", "improvement 2"],
    "follow_up_suggested": boolean,
    "follow_up_topic": "topic if suggested"
}}
"""

QUESTION_GENERATOR_PROMPT = """
Generate a challenging but fair interview question for a {target_role} position.

Candidate Profile:
- Experience: {experience_level}
- Key Skills: {skills}

Question Requirements:
- Topic: {topic}
- Difficulty: {difficulty}/10
- Type: {question_type}

Generate:
1. Question text (clear, concise)
2. Expected answer key points (3-5 bullet points)
3. Follow-up directions (how to probe deeper)
4. Common pitfalls to watch for
5. Time estimate (minutes)

Return JSON format:
{{
    "question": "question text",
    "expected_points": ["point 1", "point 2", "point 3"],
    "follow_ups": ["follow-up 1", "follow-up 2"],
    "pitfalls": ["pitfall 1", "pitfall 2"],
    "time_estimate": number,
    "difficulty": number
}}
"""

# ==================== AI Agents ====================

class InterviewerAgent:
    """Generates interview questions based on context"""
    
    def __init__(self):
        self.system_prompt = SYSTEM_PROMPTS["interviewer"]
    
    async def generate_question(
        self,
        topic: str,
        difficulty: int,
        context: Dict[str, Any],
        question_number: int
    ) -> Dict[str, Any]:
        """Generate a contextual interview question"""
        
        # In production, this would call OpenAI/Claude
        # For now, return template-based questions
        
        question_templates = {
            "system_design": [
                {
                    "question": f"Design a {topic.lower()} system. What are the key components and how would you scale it?",
                    "expected_points": [
                        "Identify key components and their responsibilities",
                        "Discuss data flow and storage requirements",
                        "Address scalability and performance considerations",
                        "Consider reliability and fault tolerance"
                    ],
                    "difficulty": difficulty
                },
                {
                    "question": f"How would you handle {topic.lower()} in a distributed system? What challenges would you face?",
                    "expected_points": [
                        "Discuss consistency models",
                        "Address network partition scenarios",
                        "Consider CAP theorem trade-offs"
                    ],
                    "difficulty": difficulty
                }
            ],
            "coding": [
                {
                    "question": f"Implement a {topic.lower()} solution. Consider edge cases and optimization.",
                    "expected_points": [
                        "Correctness of the algorithm",
                        "Time and space complexity",
                        "Edge case handling",
                        "Code readability"
                    ],
                    "difficulty": difficulty
                }
            ],
            "behavioral": [
                {
                    "question": f"Tell me about a time when you worked on {topic.lower()}. What was the challenge and how did you overcome it?",
                    "expected_points": [
                        "Specific example with context",
                        "Actions taken to solve the problem",
                        "Results and impact",
                        "Lessons learned"
                    ],
                    "difficulty": 3
                }
            ]
        }
        
        templates = question_templates.get(topic.lower(), question_templates["coding"])
        template = templates[question_number % len(templates)]
        
        return {
            "question": template["question"],
            "expected_points": template["expected_points"],
            "follow_ups": [
                "Can you elaborate on that?",
                "What would you do differently?",
                "How would you scale this?"
            ],
            "pitfalls": [
                "Giving away too much information",
                "Not asking clarifying questions",
                "Rushing to code without planning"
            ],
            "time_estimate": 5,
            "difficulty": template["difficulty"],
            "type": topic
        }


class EvaluatorAgent:
    """Evaluates interview responses"""
    
    def __init__(self):
        self.system_prompt = SYSTEM_PROMPTS["evaluator"]
    
    async def evaluate_response(
        self,
        question: str,
        question_type: str,
        expected_points: List[str],
        answer: str,
        mode: str = "text"
    ) -> Dict[str, Any]:
        """Analyze and evaluate an interview response"""
        
        # Simple heuristic evaluation
        word_count = len(answer.split())
        
        # Calculate scores based on response characteristics
        technical_score = self._evaluate_technical_content(answer, expected_points)
        completeness = min(100, 50 + (word_count // 10))
        depth = min(100, 40 + (answer.count("because") * 5) + (answer.count("why") * 3))
        communication = self._evaluate_communication(answer)
        problem_solving = self._evaluate_problem_solving(answer)
        
        overall = (technical_score + completeness + depth + communication + problem_solving) / 5
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        suggestions = []
        
        if word_count > 100:
            strengths.append("Provided a detailed response")
        else:
            weaknesses.append("Response could be more detailed")
            suggestions.append("Try to elaborate more on your thought process")
        
        if "because" in answer.lower() or "therefore" in answer.lower():
            strengths.append("Explained reasoning well")
        
        if question_type == "coding" and "O(" in answer:
            strengths.append("Considered complexity analysis")
        
        if communication > 70:
            strengths.append("Clear and structured explanation")
        else:
            suggestions.append("Practice structuring your answers")
        
        # Determine if follow-up is needed
        follow_up_suggested = overall < 60 or len(answer.split()) < 50
        follow_topic = "fundamentals" if overall < 60 else None
        
        return {
            "scores": {
                "technical_accuracy": technical_score,
                "completeness": completeness,
                "depth": depth,
                "communication": communication,
                "problem_solving": problem_solving,
                "overall": round(overall, 1)
            },
            "strengths": strengths,
            "weaknesses": weaknesses,
            "suggestions": suggestions,
            "follow_up_suggested": follow_up_suggested,
            "follow_up_topic": follow_topic
        }
    
    def _evaluate_technical_content(self, answer: str, expected_points: List[str]) -> float:
        """Evaluate technical accuracy"""
        
        score = 60.0  # Base score
        
        # Check for expected concepts
        answer_lower = answer.lower()
        
        technical_terms = {
            "system_design": ["api", "database", "cache", "server", "client", "scalability"],
            "coding": ["algorithm", "complexity", "O(", "time", "space", "optimize"],
            "behavioral": ["team", "project", "challenge", "result", "learned"]
        }
        
        # Count relevant terms found
        relevant_terms = technical_terms.get(expected_points[0].lower() if expected_points else "coding", [])
        found_terms = sum(1 for term in relevant_terms if term in answer_lower)
        
        score += min(30, found_terms * 5)
        
        return min(100, score)
    
    def _evaluate_communication(self, answer: str) -> float:
        """Evaluate communication clarity"""
        
        score = 70.0
        
        # Check for structure
        if answer.count(".") > 3:
            score += 10
        
        if any(word in answer for word in ["first", "second", "finally", "additionally"]):
            score += 15
        
        # Penalize for being too short or too long
        word_count = len(answer.split())
        if word_count < 30:
            score -= 15
        elif word_count > 500:
            score -= 10
        
        return min(100, max(0, score))
    
    def _evaluate_problem_solving(self, answer: str) -> float:
        """Evaluate problem-solving approach"""
        
        score = 65.0
        
        # Look for problem-solving language
        ps_words = ["approach", "consider", "analyze", "solution", "strategy"]
        found_ps = sum(1 for word in ps_words if word in answer.lower())
        
        score += min(25, found_ps * 5)
        
        # Check for iteration/alternatives mentioned
        if "alternative" in answer.lower() or "another way" in answer.lower():
            score += 10
        
        return min(100, score)


class CoachAgent:
    """Provides coaching and career guidance"""
    
    def __init__(self):
        self.system_prompt = SYSTEM_PROMPTS["coach"]
    
    async def generate_feedback(
        self,
        responses: List[Dict[str, Any]],
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive feedback and learning plan"""
        
        # Aggregate scores
        total_technical = sum(r.get("technical_score", 0) for r in responses)
        total_communication = sum(r.get("communication_score", 0) for r in responses)
        total_problem_solving = sum(r.get("problem_solving_score", 0) for r in responses)
        
        count = len(responses) if responses else 1
        
        avg_technical = total_technical / count
        avg_communication = total_communication / count
        avg_problem_solving = total_problem_solving / count
        overall = (avg_technical + avg_communication + avg_problem_solving) / 3
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if avg_technical >= 70:
            strengths.append("Strong technical knowledge")
        else:
            weaknesses.append("Technical fundamentals need strengthening")
        
        if avg_communication >= 70:
            strengths.append("Clear communication")
        else:
            weaknesses.append("Work on structuring your explanations")
        
        if avg_problem_solving >= 70:
            strengths.append("Good problem-solving approach")
        else:
            weaknesses.append("Practice breaking down problems systematically")
        
        # Generate recommendations
        recommendations = []
        
        if avg_technical < 60:
            recommendations.append("Focus on system design fundamentals")
            recommendations.append("Study common architectural patterns")
        
        if avg_communication < 60:
            recommendations.append("Practice explaining complex concepts simply")
            recommendations.append("Use the STAR method for behavioral questions")
        
        if avg_problem_solving < 60:
            recommendations.append("Practice coding problems daily")
            recommendations.append("Work on problem decomposition skills")
        
        recommendations.append("Schedule regular mock interviews")
        recommendations.append("Review and learn from each interview")
        
        return {
            "overall_score": round(overall, 1),
            "scores": {
                "technical": round(avg_technical, 1),
                "communication": round(avg_communication, 1),
                "problem_solving": round(avg_problem_solving, 1)
            },
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "learning_plan": self._generate_learning_plan(weaknesses)
        }
    
    def _generate_learning_plan(self, weaknesses: List[str]) -> Dict[str, Any]:
        """Generate a personalized learning plan"""
        
        plan = {
            "duration_weeks": 4,
            "focus_areas": [],
            "weekly_goals": []
        }
        
        if "Technical fundamentals" in str(weaknesses):
            plan["focus_areas"].append("System Design")
            plan["weekly_goals"].append({
                "week": 1,
                "goals": [
                    "Study scalability fundamentals",
                    "Complete 3 system design exercises"
                ]
            })
        
        if "communication" in str(weaknesses).lower():
            plan["focus_areas"].append("Communication")
            plan["weekly_goals"].append({
                "week": 2,
                "goals": [
                    "Practice explaining concepts to non-technical audience",
                    "Record yourself answering behavioral questions"
                ]
            })
        
        plan["focus_areas"] = plan["focus_areas"] or ["General Interview Prep"]
        
        return plan


class MultiAgentOrchestrator:
    """Coordinates all AI agents"""
    
    def __init__(self):
        self.interviewer = InterviewerAgent()
        self.evaluator = EvaluatorAgent()
        self.coach = CoachAgent()
    
    async def generate_interview_plan(
        self,
        request: InterviewPlanRequest
    ) -> Dict[str, Any]:
        """Generate personalized interview plan"""
        
        # Generate questions for each focus area
        questions = []
        
        for i, area in enumerate(request.focus_areas):
            question = await self.interviewer.generate_question(
                topic=area,
                difficulty=int(request.difficulty),
                context=request.dict(),
                question_number=i + 1
            )
            questions.append(question)
        
        return {
            "target_role": request.target_role,
            "difficulty": request.difficulty,
            "duration_minutes": request.duration_minutes,
            "questions": questions,
            "estimated_questions": len(questions)
        }
    
    async def analyze_response(
        self,
        request: ResponseAnalysisRequest
    ) -> Dict[str, Any]:
        """Analyze a candidate's response"""
        
        return await self.evaluator.evaluate_response(
            question=request.question,
            question_type=request.question_type,
            expected_points=request.expected_points,
            answer=request.answer,
            mode=request.mode
        )
    
    async def generate_follow_up(
        self,
        request: FollowUpRequest
    ) -> Optional[Dict[str, Any]]:
        """Generate a follow-up question based on the answer"""
        
        if request.depth_level >= 3:
            return None
        
        analysis = request.analysis
        
        # Generate follow-up based on weaknesses
        if analysis.get("follow_up_topic"):
            question = await self.interviewer.generate_question(
                topic=analysis["follow_up_topic"],
                difficulty=max(1, request.depth_level - 1),
                context={"original": request.original_question},
                question_number=request.depth_level + 1
            )
            
            return {
                "question": question["question"],
                "type": "follow_up",
                "depth_level": request.depth_level + 1
            }
        
        return None
    
    async def generate_feedback(
        self,
        request: FeedbackRequest
    ) -> Dict[str, Any]:
        """Generate comprehensive feedback"""
        
        return await self.coach.generate_feedback(
            responses=request.session_responses,
            user_profile=request.user_profile
        )


# ==================== FastAPI App ====================

app = FastAPI(title="AI Engine", version="1.0.0")
orchestrator = MultiAgentOrchestrator()

@app.post("/v1/ai/interview-plan")
async def create_interview_plan(request: InterviewPlanRequest):
    """Generate a personalized interview plan"""
    
    plan = await orchestrator.generate_interview_plan(request)
    
    return plan

@app.post("/v1/ai/question")
async def generate_question(request: QuestionGenerateRequest):
    """Generate an interview question"""
    
    question = await orchestrator.interviewer.generate_question(
        topic=request.topic,
        difficulty=request.difficulty,
        context=request.context or {},
        question_number=request.question_number
    )
    
    return question

@app.post("/v1/ai/analyze")
async def analyze_response(request: ResponseAnalysisRequest):
    """Analyze a candidate's response"""
    
    analysis = await orchestrator.analyze_response(request)
    
    return analysis

@app.post("/v1/ai/follow-up")
async def generate_follow_up(request: FollowUpRequest):
    """Generate a follow-up question"""
    
    follow_up = await orchestrator.generate_follow_up(request)
    
    if follow_up:
        return follow_up
    else:
        return {"message": "No follow-up needed", "type": "complete"}

@app.post("/v1/ai/feedback")
async def generate_feedback(request: FeedbackRequest):
    """Generate comprehensive feedback"""
    
    feedback = await orchestrator.generate_feedback(request)
    
    return feedback

# ==================== Prompt Management ====================

@app.get("/v1/ai/prompts/{agent_role}")
async def get_prompt(agent_role: AgentRole):
    """Get system prompt for an agent"""
    
    return {
        "role": agent_role.value,
        "prompt": SYSTEM_PROMPTS.get(agent_role.value, "")
    }

@app.put("/v1/ai/prompts/{agent_role}")
async def update_prompt(agent_role: AgentRole, prompt: str):
    """Update system prompt for an agent"""
    
    SYSTEM_PROMPTS[agent_role.value] = prompt
    
    # Cache in Redis
    r = await get_redis()
    await r.set(f"prompt:{agent_role.value}", prompt)
    
    return {"status": "updated"}

# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-engine"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
