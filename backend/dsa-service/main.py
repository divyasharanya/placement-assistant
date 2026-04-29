# """
# DSA Service - Code Execution and Evaluation
# Go-based microservice for running and evaluating code submissions
# """
# import sys, os
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
# import os
# import json
# import asyncio
# import re
# from datetime import datetime
# from typing import Optional, List, Dict, Any
# from uuid import UUID, uuid4
# from enum import Enum

# from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status, Query
# from fastapi.responses import JSONResponse
# from pydantic import BaseModel, Field
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
# from sqlalchemy import select

# from database.models import (
#     DSAProblem, DSASubmission, User, 
#     DSADifficulty, SubmissionStatus
# )

# # Import curated problems data
# from problems_data import (
#     CURATED_PROBLEMS,
#     get_daily_problem,
#     get_problem_by_slug,
#     get_problems,
#     TOPICS
# )

# # ==================== Configuration ====================

# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/aimock")
# REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# # Language configurations
# LANGUAGE_CONFIGS = {
#     "python": {
#         "image": "python:3.11-slim",
#         "compile_cmd": None,
#         "run_cmd": "python3 {file}",
#         "timeout": 5,
#         "memory_limit": 256
#     },
#     "javascript": {
#         "image": "node:20-slim",
#         "compile_cmd": None,
#         "run_cmd": "node {file}",
#         "timeout": 5,
#         "memory_limit": 256
#     },
#     "java": {
#         "image": "openjdk:17-slim",
#         "compile_cmd": "javac {file}",
#         "run_cmd": "java Main",
#         "timeout": 10,
#         "memory_limit": 512
#     },
#     "cpp": {
#         "image": "gcc:12-slim",
#         "compile_cmd": "g++ -o main {file}",
#         "run_cmd": "./main",
#         "timeout": 5,
#         "memory_limit": 256
#     },
#     "go": {
#         "image": "golang:1.21-slim",
#         "compile_cmd": None,
#         "run_cmd": "go run {file}",
#         "timeout": 5,
#         "memory_limit": 256
#     }
# }

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

# # ==================== Pydantic Models ====================

# class SubmissionCreate(BaseModel):
#     problem_id: UUID
#     code: str
#     language: str

# class SubmissionResponse(BaseModel):
#     id: UUID
#     status: str
#     runtime_ms: Optional[int]
#     memory_mb: Optional[float]
#     test_cases_passed: Optional[int]
#     total_test_cases: Optional[int]

# class ProblemCreate(BaseModel):
#     title: str
#     description: str
#     difficulty: DSADifficulty
#     topics: Optional[List[str]] = None
#     time_complexity_expected: Optional[str] = None
#     space_complexity_expected: Optional[str] = None
#     hints: Optional[List[str]] = None
#     test_cases: List[Dict[str, Any]]

# class ExecutionResult(BaseModel):
#     status: SubmissionStatus
#     output: str
#     expected: Optional[str] = None
#     runtime_ms: int = 0
#     memory_mb: float = 0.0
#     error: Optional[str] = None

# # ==================== Code Executor ====================

# class CodeExecutor:
#     """Mock code executor - in production, this would use Docker containers"""
    
#     def __init__(self):
#         self.language_configs = LANGUAGE_CONFIGS
    
#     async def execute(
#         self,
#         code: str,
#         language: str,
#         test_cases: List[Dict[str, Any]]
#     ) -> Dict[str, Any]:
#         """Execute code against test cases"""
        
#         if language not in self.language_configs:
#             return {
#                 "status": SubmissionStatus.COMPILATION_ERROR,
#                 "error": f"Unsupported language: {language}"
#             }
        
#         config = self.language_configs[language]
#         results = []
        
#         # Mock execution - in production, would run in Docker
#         for i, test_case in enumerate(test_cases):
#             result = await self._execute_single_test(
#                 code, language, test_case, config
#             )
#             results.append(result)
            
#             if result["status"] != SubmissionStatus.ACCEPTED:
#                 break
        
#         # Aggregate results
#         passed = sum(1 for r in results if r["status"] == SubmissionStatus.ACCEPTED)
#         total = len(test_cases)
        
#         return {
#             "status": SubmissionStatus.ACCEPTED if passed == total else SubmissionStatus.WRONG_ANSWER,
#             "test_results": results,
#             "passed": passed,
#             "total": total,
#             "runtime_ms": max(r.get("runtime_ms", 0) for r in results),
#             "memory_mb": max(r.get("memory_mb", 0) for r in results)
#         }
    
#     async def _execute_single_test(
#         self,
#         code: str,
#         language: str,
#         test_case: Dict[str, Any],
#         config: Dict
#     ) -> Dict[str, Any]:
#         """Execute a single test case"""
        
#         # Mock execution - would actually run code in Docker container
#         input_data = test_case.get("input", "")
#         expected_output = test_case.get("output", "")
        
#         # Simulate code execution
#         # In production, this would:
#         # 1. Create isolated container
#         # 2. Mount code file
#         # 3. Run with input
#         # 4. Capture output and metrics
#         # 5. Clean up
        
#         # For now, do simple syntax check and mock output
#         try:
#             # Check for basic syntax errors
#             if language == "python":
#                 compile(code, "<string>", "exec")
                
#                 # Mock execution - check if we can parse input and produce output
#                 # In production, actually run the code
#                 output = self._mock_execute(code, input_data, expected_output)
                
#                 if output.strip() == expected_output.strip():
#                     return {
#                         "status": SubmissionStatus.ACCEPTED,
#                         "output": output,
#                         "expected": expected_output,
#                         "runtime_ms": 50,
#                         "memory_mb": 25.0
#                     }
#                 else:
#                     return {
#                         "status": SubmissionStatus.WRONG_ANSWER,
#                         "output": output,
#                         "expected": expected_output,
#                         "runtime_ms": 50,
#                         "memory_mb": 25.0
#                     }
            
#             elif language == "javascript":
#                 # Check syntax
#                 if "function" not in code and "=>" not in code:
#                     return {
#                         "status": SubmissionStatus.COMPILATION_ERROR,
#                         "error": "Invalid JavaScript syntax"
#                     }
                
#                 output = self._mock_execute(code, input_data, expected_output)
                
#                 return {
#                     "status": SubmissionStatus.ACCEPTED if output.strip() == expected_output.strip() else SubmissionStatus.WRONG_ANSWER,
#                     "output": output,
#                     "expected": expected_output,
#                     "runtime_ms": 50,
#                     "memory_mb": 30.0
#                 }
            
#             else:
#                 # For other languages, assume correct
#                 return {
#                     "status": SubmissionStatus.ACCEPTED,
#                     "output": expected_output,
#                     "expected": expected_output,
#                     "runtime_ms": 100,
#                     "memory_mb": 50.0
#                 }
                
#         except SyntaxError as e:
#             return {
#                 "status": SubmissionStatus.COMPILATION_ERROR,
#                 "error": f"Syntax error: {str(e)}",
#                 "runtime_ms": 0,
#                 "memory_mb": 0
#             }
#         except Exception as e:
#             return {
#                 "status": SubmissionStatus.RUNTIME_ERROR,
#                 "error": str(e),
#                 "runtime_ms": 0,
#                 "memory_mb": 0
#             }
    
#     def _mock_execute(self, code: str, input_data: str, expected: str) -> str:
#         """Mock code execution"""
        
#         # This is a simplified mock - in production would actually execute
#         # Try to find print statements and extract output
        
#         # Simple regex to find print statements
#         print_pattern = r'print\s*\(\s*(.+?)\s*\)'
#         matches = re.findall(print_pattern, code)
        
#         if matches:
#             # Get last print statement result
#             last_match = matches[-1]
            
#             # Try to evaluate simple expressions
#             if "input()" in code:
#                 # If code uses input, use test input
#                 return expected  # Assume correct
            
#             try:
#                 # Simple evaluation
#                 result = eval(last_match, {"__builtins__": {}}, {})
#                 return str(result)
#             except:
#                 return expected
        
#         return expected  # Return expected for mock


# class CodeAnalyzer:
#     """Analyze code quality and complexity"""
    
#     def analyze_complexity(self, code: str, language: str) -> Dict[str, Any]:
#         """Calculate time and space complexity"""
        
#         # Simple heuristics
#         time_complexity = "O(1)"
#         space_complexity = "O(1)"
        
#         # Count loops
#         loop_patterns = [
#             r'\bfor\b', r'\bwhile\b', r'\bmap\b', r'\bfilter\b', 
#             r'\breduce\b', r'\bfor\s+each\b'
#         ]
        
#         loop_count = sum(len(re.findall(p, code)) for p in loop_patterns)
        
#         if loop_count >= 3:
#             time_complexity = "O(n^2)"
#         elif loop_count == 2:
#             time_complexity = "O(n)"
#         elif loop_count == 1:
#             time_complexity = "O(n)"
        
#         # Check for recursion
#         if re.search(r'\bdef\s+\w+\s*\([^)]*\)\s*:', code):
#             if code.count("def ") > 1:
#                 time_complexity = "O(2^n)"  # Likely recursive
        
#         # Check for data structures
#         if any(ds in code.lower() for ds in ["list", "array", "dict", "set", "hash", "map"]):
#             space_complexity = "O(n)"
        
#         return {
#             "time_complexity": time_complexity,
#             "space_complexity": space_complexity,
#             "suggestions": self._get_optimization_suggestions(time_complexity)
#         }
    
#     def _get_optimization_suggestions(self, complexity: str) -> List[str]:
#         """Get optimization suggestions"""
        
#         suggestions = []
        
#         if complexity == "O(n^2)":
#             suggestions.append("Consider using a hash map to reduce time complexity")
#             suggestions.append("Can you break down nested loops?")
#         elif complexity == "O(2^n)":
#             suggestions.append("Consider dynamic programming to optimize recursive solutions")
        
#         if not suggestions:
#             suggestions.append("Good complexity! Consider edge cases")
        
#         return suggestions
    
#     def detect_plagiarism(self, code: str) -> Dict[str, Any]:
#         """Simple plagiarism detection"""
        
#         # In production, would use AST similarity and embeddings
#         # For now, simple heuristics
        
#         score = 0.0
        
#         # Check for common patterns
#         if len(code) < 50:
#             score = 0.3  # Too short to analyze
        
#         # Check for standard boilerplate
#         if "if __name__" in code:
#             score += 0.2
        
#         # Check for comments
#         comment_ratio = code.count("#") / max(len(code.split()), 1)
#         if comment_ratio > 0.1:
#             score += 0.2
        
#         return {
#             "score": min(score, 1.0),
#             "is_suspicious": score > 0.7,
#             "details": "Simple pattern analysis"
#         }


# # ==================== FastAPI App ====================

# app = FastAPI(title="DSA Service", version="1.0.0")
# executor = CodeExecutor()
# analyzer = CodeAnalyzer()

# async def get_current_user_id() -> UUID:
#     """In production, extract from JWT token"""
#     return uuid4()

# @app.post("/v1/dsa/problems", status_code=status.HTTP_201_CREATED)
# async def create_problem(
#     problem: ProblemCreate,
#     db: AsyncSession = Depends(get_db),
#     user_id: UUID = Depends(get_current_user_id)
# ):
#     """Create a new DSA problem"""
    
#     # Generate slug from title
#     slug = problem.title.lower().replace(" ", "-")
#     slug = re.sub(r'[^a-z0-9-]', '', slug)
    
#     dsa_problem = DSAProblem(
#         title=problem.title,
#         slug=slug,
#         description=problem.description,
#         difficulty=problem.difficulty,
#         topics=problem.topics or [],
#         time_complexity_expected=problem.time_complexity_expected,
#         space_complexity_expected=problem.space_complexity_expected,
#         hints=problem.hints or [],
#         test_cases=problem.test_cases,
#         created_by=user_id
#     )
    
#     db.add(dsa_problem)
#     await db.commit()
    
#     return {
#         "id": str(dsa_problem.id),
#         "slug": dsa_problem.slug,
#         "status": "created"
#     }

# @app.get("/v1/dsa/problems")
# async def list_problems(
#     difficulty: Optional[DSADifficulty] = None,
#     topic: Optional[str] = None,
#     limit: int = 20,
#     offset: int = 0,
#     db: AsyncSession = Depends(get_db)
# ):
#     """List DSA problems with filters"""
    
#     query = select(DSAProblem)
    
#     if difficulty:
#         query = query.where(DSAProblem.difficulty == difficulty)
    
#     query = query.limit(limit).offset(offset).order_by(DSAProblem.created_at.desc())
    
#     result = await db.execute(query)
#     problems = result.scalars().all()
    
#     return {
#         "problems": [
#             {
#                 "id": str(p.id),
#                 "title": p.title,
#                 "slug": p.slug,
#                 "difficulty": p.difficulty.value,
#                 "topics": p.topics,
#                 "companies_asked": p.companies_asked,
#                 "frequency_score": p.frequency_score
#             }
#             for p in problems
#         ],
#         "total": len(problems)
#     }

# @app.get("/v1/dsa/problems/{slug}")
# async def get_problem(
#     slug: str,
#     db: AsyncSession = Depends(get_db)
# ):
#     """Get problem details"""
    
#     # First try to get from curated problems
#     curated_problem = get_problem_by_slug(slug)
#     if curated_problem:
#         return curated_problem
    
#     # Fall back to database
#     result = await db.execute(select(DSAProblem).where(DSAProblem.slug == slug))
#     problem = result.scalar_one_or_none()
    
#     if not problem:
#         raise HTTPException(status_code=404, detail="Problem not found")
    
#     return {
#         "id": str(problem.id),
#         "title": problem.title,
#         "slug": problem.slug,
#         "description": problem.description,
#         "difficulty": problem.difficulty.value,
#         "topics": problem.topics,
#         "companies_asked": problem.companies_asked,
#         "time_complexity_expected": problem.time_complexity_expected,
#         "space_complexity_expected": problem.space_complexity_expected,
#         "hints": problem.hints,
#         "test_cases": [
#             {"input": tc.get("input"), "output": tc.get("output")}
#             for tc in problem.test_cases[:3]  # Only visible test cases
#         ]
#     }

# # ==================== NEW PROBLEM LIBRARY API ====================

# @app.get("/api/problems")
# async def list_problems_api(
#     difficulty: Optional[str] = None,
#     topic: Optional[str] = None,
#     search: Optional[str] = None,
#     limit: int = Query(20, ge=1, le=100),
#     offset: int = Query(0, ge=0)
# ):
#     """
#     List problems with optional filters.
    
#     - **difficulty**: Filter by difficulty (easy, medium, hard)
#     - **topic**: Filter by topic/category
#     - **search**: Search by problem title
#     - **limit**: Number of problems to return
#     - **offset**: Number of problems to skip
#     """
#     result = get_problems(
#         difficulty=difficulty,
#         topic=topic,
#         search=search,
#         limit=limit,
#         offset=offset
#     )
    
#     # Format response
#     return {
#         "problems": [
#             {
#                 "id": p["id"],
#                 "title": p["title"],
#                 "slug": p["slug"],
#                 "difficulty": p["difficulty"].value if hasattr(p["difficulty"], 'value') else p["difficulty"],
#                 "category": p["category"],
#                 "tags": p["tags"],
#                 "platformLink": p["platformLink"],
#                 "companies_asked": p.get("companies_asked", [])
#             }
#             for p in result["problems"]
#         ],
#         "total": result["total"],
#         "limit": result["limit"],
#         "offset": result["offset"]
#     }

# @app.get("/api/problems/{slug}")
# async def get_problem_api(
#     slug: str
# ):
#     """
#     Get detailed problem information by slug.
#     """
#     problem = get_problem_by_slug(slug)
    
#     if not problem:
#         raise HTTPException(status_code=404, detail="Problem not found")
    
#     # Format response
#     return {
#         "id": problem["id"],
#         "title": problem["title"],
#         "slug": problem["slug"],
#         "difficulty": problem["difficulty"].value if hasattr(problem["difficulty"], 'value') else problem["difficulty"],
#         "category": problem["category"],
#         "tags": problem["tags"],
#         "description": problem["description"],
#         "constraints": problem.get("constraints", []),
#         "inputFormat": problem.get("inputFormat", ""),
#         "outputFormat": problem.get("outputFormat", ""),
#         "exampleInput": problem.get("exampleInput", ""),
#         "exampleOutput": problem.get("exampleOutput", ""),
#         "explanation": problem.get("explanation", ""),
#         "platformLink": problem["platformLink"],
#         "companies_asked": problem.get("companies_asked", [])
#     }

# @app.get("/api/daily-problem")
# async def get_daily_problem_api():
#     """
#     Get the daily recommended problem.
#     Automatically changes based on the current day.
#     """
#     return get_daily_problem()

# @app.get("/api/topics")
# async def get_topics():
#     """
#     Get list of all available topics/categories.
#     """
#     return {
#         "topics": TOPICS
#     }

# @app.get("/api/difficulties")
# async def get_difficulties():
#     """
#     Get list of all difficulty levels.
#     """
#     return {
#         "difficulties": [
#             {"value": "easy", "label": "Easy", "count": len([p for p in CURATED_PROBLEMS if p["difficulty"].value == "easy"])},
#             {"value": "medium", "label": "Medium", "count": len([p for p in CURATED_PROBLEMS if p["difficulty"].value == "medium"])},
#             {"value": "hard", "label": "Hard", "count": len([p for p in CURATED_PROBLEMS if p["difficulty"].value == "hard"])}
#         ]
#     }

# @app.post("/v1/dsa/problems/{slug}/submit")
# async def submit_solution(
#     slug: str,
#     submission: SubmissionCreate,
#     db: AsyncSession = Depends(get_db),
#     background_tasks: BackgroundTasks = None,
#     user_id: UUID = Depends(get_current_user_id)
# ):
#     """Submit code solution"""
    
#     # Get problem
#     result = await db.execute(select(DSAProblem).where(DSAProblem.slug == slug))
#     problem = result.scalar_one_or_none()
    
#     if not problem:
#         raise HTTPException(status_code=404, detail="Problem not found")
    
#     # Check submission limit
#     count_result = await db.execute(
#         select(DSASubmission)
#         .where(
#             DSASubmission.user_id == user_id,
#             DSASubmission.problem_id == problem.id
#         )
#     )
#     previous_submissions = count_result.scalars().all()
    
#     # Create submission record
#     submission_record = DSASubmission(
#         user_id=user_id,
#         problem_id=problem.id,
#         code=submission.code,
#         language=submission.language,
#         status=SubmissionStatus.RUNNING,
#         attempts_count=len(previous_submissions) + 1
#     )
    
#     db.add(submission_record)
#     await db.flush()
    
#     # Execute code
#     test_cases = problem.test_cases
    
#     execution_result = await executor.execute(
#         submission.code,
#         submission.language,
#         test_cases
#     )
    
#     # Update submission
#     submission_record.status = execution_result["status"]
#     submission_record.runtime_ms = execution_result.get("runtime_ms")
#     submission_record.memory_mb = execution_result.get("memory_mb")
#     submission_record.test_cases_passed = execution_result.get("passed")
#     submission_record.total_test_cases = execution_result.get("total")
    
#     if execution_result.get("test_results"):
#         # Get first failed test case
#         failed_tests = [r for r in execution_result["test_results"] if r["status"] != SubmissionStatus.ACCEPTED]
#         if failed_tests:
#             submission_record.failed_test_case = failed_tests[0]
    
#     await db.commit()
    
#     return {
#         "id": str(submission_record.id),
#         "status": submission_record.status.value,
#         "test_cases_passed": submission_record.test_cases_passed,
#         "total_test_cases": submission_record.total_test_cases,
#         "runtime_ms": submission_record.runtime_ms,
#         "memory_mb": submission_record.memory_mb
#     }

# @app.get("/v1/dsa/submissions/{submission_id}")
# async def get_submission(
#     submission_id: UUID,
#     db: AsyncSession = Depends(get_db)
# ):
#     """Get submission details"""
    
#     result = await db.execute(select(DSASubmission).where(DSASubmission.id == submission_id))
#     submission = result.scalar_one_or_none()
    
#     if not submission:
#         raise HTTPException(status_code=404, detail="Submission not found")
    
#     return {
#         "id": str(submission.id),
#         "problem_id": str(submission.problem_id),
#         "status": submission.status.value,
#         "code": submission.code,
#         "language": submission.language,
#         "runtime_ms": submission.runtime_ms,
#         "memory_mb": submission.memory_mb,
#         "test_cases_passed": submission.test_cases_passed,
#         "total_test_cases": submission.total_test_cases,
#         "failed_test_case": submission.failed_test_case,
#         "created_at": submission.created_at.isoformat()
#     }

# @app.get("/v1/dsa/problems/{slug}/submissions")
# async def get_user_submissions(
#     slug: str,
#     db: AsyncSession = Depends(get_db),
#     user_id: UUID = Depends(get_current_user_id)
# ):
#     """Get user's submissions for a problem"""
    
#     # Get problem
#     result = await db.execute(select(DSAProblem).where(DSAProblem.slug == slug))
#     problem = result.scalar_one_or_none()
    
#     if not problem:
#         raise HTTPException(status_code=404, detail="Problem not found")
    
#     # Get submissions
#     sub_result = await db.execute(
#         select(DSASubmission)
#         .where(
#             DSASubmission.user_id == user_id,
#             DSASubmission.problem_id == problem.id
#         )
#         .order_by(DSASubmission.created_at.desc())
#     )
#     submissions = sub_result.scalars().all()
    
#     return {
#         "submissions": [
#             {
#                 "id": str(s.id),
#                 "status": s.status.value,
#                 "language": s.language,
#                 "test_cases_passed": s.test_cases_passed,
#                 "total_test_cases": s.total_test_cases,
#                 "runtime_ms": s.runtime_ms,
#                 "attempts": s.attempts_count,
#                 "created_at": s.created_at.isoformat()
#             }
#             for s in submissions
#         ]
#     }

# @app.post("/v1/dsa/problems/{slug}/hint")
# async def get_hint(
#     slug: str,
#     current_hint_level: int = 0,
#     db: AsyncSession = Depends(get_db)
# ):
#     """Get a hint for the problem"""
    
#     result = await db.execute(select(DSAProblem).where(DSAProblem.slug == slug))
#     problem = result.scalar_one_or_none()
    
#     if not problem:
#         raise HTTPException(status_code=404, detail="Problem not found")
    
#     hints = problem.hints or []
    
#     if current_hint_level >= len(hints):
#         return {
#             "hint": "No more hints available",
#             "hint_level": current_hint_level
#         }
    
#     return {
#         "hint": hints[current_hint_level],
#         "hint_level": current_hint_level + 1
#     }

# @app.get("/v1/dsa/analyze/{submission_id}")
# async def analyze_code(
#     submission_id: UUID,
#     db: AsyncSession = Depends(get_db)
# ):
#     """Get code analysis for a submission"""
    
#     result = await db.execute(select(DSASubmission).where(DSASubmission.id == submission_id))
#     submission = result.scalar_one_or_none()
    
#     if not submission:
#         raise HTTPException(status_code=404, detail="Submission not found")
    
#     # Analyze code
#     complexity = analyzer.analyze_complexity(submission.code, submission.language)
#     plagiarism = analyzer.detect_plagiarism(submission.code)
    
#     return {
#         "complexity": complexity,
#         "plagiarism": plagiarism
#     }

# @app.get("/health")
# async def health_check():
#     return {"status": "healthy", "service": "dsa"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8004)


#original code in the above
"""
DSA Practice Service - problems_service.py
A clean, standalone FastAPI backend for the practice page.
Run: python problems_service.py
Port: 8004
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from datetime import date
from enum import Enum

# ─────────────────────────────────────────────
#  DATA
# ─────────────────────────────────────────────

class DSADifficulty(str, Enum):
    EASY   = "easy"
    MEDIUM = "medium"
    HARD   = "hard"

TOPICS = [
    "Arrays", "Strings", "Linked List", "Trees", "Graphs",
    "Dynamic Programming", "Recursion", "Stack", "Queue",
    "Hash Tables", "Two Pointers", "Sliding Window",
    "Binary Search", "Greedy", "Backtracking", "Heap",
    "Sorting", "Divide and Conquer", "Bit Manipulation", "Math",
]

PROBLEMS: List[Dict[str, Any]] = [
    # ── EASY ──────────────────────────────────────────────────────
    {
        "id": "two-sum", "title": "Two Sum", "slug": "two-sum",
        "difficulty": DSADifficulty.EASY, "category": "Arrays",
        "tags": ["Arrays", "Hash Tables"],
        "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.",
        "constraints": ["2 <= nums.length <= 10^4", "-10^9 <= nums[i] <= 10^9", "Only one valid answer exists."],
        "inputFormat": "Array of integers and a target integer.",
        "outputFormat": "Indices of the two numbers that sum to target.",
        "exampleInput": "nums = [2,7,11,15], target = 9",
        "exampleOutput": "[0,1]",
        "explanation": "nums[0] + nums[1] == 9, so return [0, 1].",
        "platformLink": "https://leetcode.com/problems/two-sum/",
        "companies_asked": ["Google", "Amazon", "Apple", "Microsoft", "Meta"],
        "frequency_score": 0.95, "acceptance_rate": 49.1,
        "hints": ["Try using a hash map to store complements.", "For each number, check if target - num exists in the map."],
        "time_complexity": "O(n)", "space_complexity": "O(n)",
    },
    {
        "id": "reverse-string", "title": "Reverse String", "slug": "reverse-string",
        "difficulty": DSADifficulty.EASY, "category": "Strings",
        "tags": ["Strings", "Two Pointers"],
        "description": "Write a function that reverses a string. The input string is given as an array of characters s.\n\nYou must do this by modifying the input array in-place with O(1) extra memory.",
        "constraints": ["1 <= s.length <= 10^5", "s[i] is a printable ascii character."],
        "inputFormat": "Array of characters s.", "outputFormat": "Reversed array in-place.",
        "exampleInput": 's = ["h","e","l","l","o"]', "exampleOutput": '["o","l","l","e","h"]',
        "explanation": "Use two pointers from both ends and swap.",
        "platformLink": "https://leetcode.com/problems/reverse-string/",
        "companies_asked": ["Amazon", "Microsoft", "Apple"],
        "frequency_score": 0.82, "acceptance_rate": 75.4,
        "hints": ["Use two pointers."], "time_complexity": "O(n)", "space_complexity": "O(1)",
    },
    {
        "id": "valid-parentheses", "title": "Valid Parentheses", "slug": "valid-parentheses",
        "difficulty": DSADifficulty.EASY, "category": "Stack",
        "tags": ["Stack", "Strings"],
        "description": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.\n\nAn input string is valid if:\n1. Open brackets must be closed by the same type.\n2. Open brackets must be closed in the correct order.\n3. Every close bracket has a corresponding open bracket.",
        "constraints": ["1 <= s.length <= 10^4", "s consists of parentheses only '()[]{}'."],
        "inputFormat": "String of parentheses.", "outputFormat": "true or false.",
        "exampleInput": 's = "()"', "exampleOutput": "true",
        "explanation": "Parentheses are properly balanced.",
        "platformLink": "https://leetcode.com/problems/valid-parentheses/",
        "companies_asked": ["Amazon", "Google", "Meta", "Microsoft"],
        "frequency_score": 0.90, "acceptance_rate": 40.7,
        "hints": ["Use a stack. Push opening brackets, pop on closing."],
        "time_complexity": "O(n)", "space_complexity": "O(n)",
    },
    {
        "id": "best-time-stock", "title": "Best Time to Buy and Sell Stock", "slug": "best-time-stock",
        "difficulty": DSADifficulty.EASY, "category": "Arrays",
        "tags": ["Arrays", "Dynamic Programming"],
        "description": "You are given an array prices where prices[i] is the price of a stock on the ith day.\n\nMaximize profit by choosing a single day to buy and a future day to sell. Return maximum profit or 0 if no profit is possible.",
        "constraints": ["1 <= prices.length <= 10^5", "0 <= prices[i] <= 10^4"],
        "inputFormat": "Array of stock prices.", "outputFormat": "Maximum profit.",
        "exampleInput": "prices = [7,1,5,3,6,4]", "exampleOutput": "5",
        "explanation": "Buy on day 2 (price=1), sell day 5 (price=6). Profit = 5.",
        "platformLink": "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/",
        "companies_asked": ["Amazon", "Meta", "Microsoft", "Apple"],
        "frequency_score": 0.88, "acceptance_rate": 54.3,
        "hints": ["Track minimum price seen so far."],
        "time_complexity": "O(n)", "space_complexity": "O(1)",
    },
    {
        "id": "maximum-subarray", "title": "Maximum Subarray", "slug": "maximum-subarray",
        "difficulty": DSADifficulty.EASY, "category": "Arrays",
        "tags": ["Arrays", "Dynamic Programming", "Divide and Conquer"],
        "description": "Given an integer array nums, find the subarray with the largest sum and return its sum.",
        "constraints": ["1 <= nums.length <= 10^5", "-10^4 <= nums[i] <= 10^4"],
        "inputFormat": "Array of integers.", "outputFormat": "Maximum subarray sum.",
        "exampleInput": "nums = [-2,1,-3,4,-1,2,1,-5,4]", "exampleOutput": "6",
        "explanation": "[4,-1,2,1] has the largest sum 6.",
        "platformLink": "https://leetcode.com/problems/maximum-subarray/",
        "companies_asked": ["Amazon", "Microsoft", "Apple", "LinkedIn"],
        "frequency_score": 0.92, "acceptance_rate": 49.8,
        "hints": ["Kadane's algorithm: track current sum and max sum."],
        "time_complexity": "O(n)", "space_complexity": "O(1)",
    },
    {
        "id": "valid-palindrome", "title": "Valid Palindrome", "slug": "valid-palindrome",
        "difficulty": DSADifficulty.EASY, "category": "Strings",
        "tags": ["Strings", "Two Pointers"],
        "description": "A phrase is a palindrome if, after converting to lowercase and removing non-alphanumeric characters, it reads the same forward and backward.\n\nGiven string s, return true if it is a palindrome.",
        "constraints": ["1 <= s.length <= 2*10^5"],
        "inputFormat": "String s.", "outputFormat": "true or false.",
        "exampleInput": 's = "A man, a plan, a canal: Panama"', "exampleOutput": "true",
        "explanation": '"amanaplanacanalpanama" is a palindrome.',
        "platformLink": "https://leetcode.com/problems/valid-palindrome/",
        "companies_asked": ["Meta", "Microsoft", "Amazon"],
        "frequency_score": 0.78, "acceptance_rate": 43.1,
        "hints": ["Use two pointers from both ends, skip non-alphanumeric."],
        "time_complexity": "O(n)", "space_complexity": "O(1)",
    },
    {
        "id": "linked-list-cycle", "title": "Linked List Cycle", "slug": "linked-list-cycle",
        "difficulty": DSADifficulty.EASY, "category": "Linked List",
        "tags": ["Linked List", "Two Pointers", "Hash Tables"],
        "description": "Given head of a linked list, determine if the linked list has a cycle.\n\nReturn true if there is a cycle, otherwise false.",
        "constraints": ["0 <= number of nodes <= 10^4", "-10^5 <= Node.val <= 10^5"],
        "inputFormat": "Head of a linked list.", "outputFormat": "true or false.",
        "exampleInput": "head = [3,2,0,-4], pos = 1", "exampleOutput": "true",
        "explanation": "Tail connects to node at index 1.",
        "platformLink": "https://leetcode.com/problems/linked-list-cycle/",
        "companies_asked": ["Amazon", "Google", "Microsoft", "Apple"],
        "frequency_score": 0.82, "acceptance_rate": 46.5,
        "hints": ["Floyd's cycle detection — slow and fast pointers."],
        "time_complexity": "O(n)", "space_complexity": "O(1)",
    },
    {
        "id": "merge-sorted-array", "title": "Merge Sorted Array", "slug": "merge-sorted-array",
        "difficulty": DSADifficulty.EASY, "category": "Arrays",
        "tags": ["Arrays", "Two Pointers", "Sorting"],
        "description": "Given two sorted integer arrays nums1 and nums2, merge nums2 into nums1 as one sorted array in-place.",
        "constraints": ["nums1.length == m + n", "0 <= m, n <= 200"],
        "inputFormat": "Two sorted arrays nums1, nums2 and sizes m, n.", "outputFormat": "Merged sorted array in nums1.",
        "exampleInput": "nums1 = [1,2,3,0,0,0], m = 3, nums2 = [2,5,6], n = 3", "exampleOutput": "[1,2,2,3,5,6]",
        "explanation": "Merge from the end to avoid overwriting.",
        "platformLink": "https://leetcode.com/problems/merge-sorted-array/",
        "companies_asked": ["Amazon", "Microsoft", "Google"],
        "frequency_score": 0.75, "acceptance_rate": 47.0,
        "hints": ["Start filling from the end of nums1."],
        "time_complexity": "O(m+n)", "space_complexity": "O(1)",
    },
    {
        "id": "climbing-stairs", "title": "Climbing Stairs", "slug": "climbing-stairs",
        "difficulty": DSADifficulty.EASY, "category": "Dynamic Programming",
        "tags": ["Dynamic Programming", "Math", "Recursion"],
        "description": "You are climbing a staircase. It takes n steps to reach the top. Each time you can climb 1 or 2 steps. How many distinct ways can you climb to the top?",
        "constraints": ["1 <= n <= 45"],
        "inputFormat": "Integer n.", "outputFormat": "Number of distinct ways.",
        "exampleInput": "n = 3", "exampleOutput": "3",
        "explanation": "1+1+1, 1+2, 2+1 — three ways.",
        "platformLink": "https://leetcode.com/problems/climbing-stairs/",
        "companies_asked": ["Amazon", "Google", "Apple", "Adobe"],
        "frequency_score": 0.87, "acceptance_rate": 51.7,
        "hints": ["This is essentially Fibonacci."],
        "time_complexity": "O(n)", "space_complexity": "O(1)",
    },
    {
        "id": "binary-search", "title": "Binary Search", "slug": "binary-search",
        "difficulty": DSADifficulty.EASY, "category": "Arrays",
        "tags": ["Arrays", "Binary Search"],
        "description": "Given an array of integers nums sorted in ascending order, and an integer target, write a function to search target in nums. If target exists, return its index. Otherwise, return -1.",
        "constraints": ["1 <= nums.length <= 10^4", "All nums are unique.", "nums is sorted ascending."],
        "inputFormat": "Sorted array nums and target integer.", "outputFormat": "Index of target or -1.",
        "exampleInput": "nums = [-1,0,3,5,9,12], target = 9", "exampleOutput": "4",
        "explanation": "9 exists at index 4.",
        "platformLink": "https://leetcode.com/problems/binary-search/",
        "companies_asked": ["Google", "Amazon", "Microsoft"],
        "frequency_score": 0.80, "acceptance_rate": 55.6,
        "hints": ["Use left and right pointers. Mid = (l+r)//2."],
        "time_complexity": "O(log n)", "space_complexity": "O(1)",
    },

    # ── MEDIUM ─────────────────────────────────────────────────────
    {
        "id": "longest-substring", "title": "Longest Substring Without Repeating Characters", "slug": "longest-substring",
        "difficulty": DSADifficulty.MEDIUM, "category": "Strings",
        "tags": ["Hash Tables", "Strings", "Sliding Window"],
        "description": "Given a string s, find the length of the longest substring without repeating characters.",
        "constraints": ["0 <= s.length <= 5*10^4"],
        "inputFormat": "String s.", "outputFormat": "Length of longest substring.",
        "exampleInput": 's = "abcabcbb"', "exampleOutput": "3",
        "explanation": '"abc" is the answer with length 3.',
        "platformLink": "https://leetcode.com/problems/longest-substring-without-repeating-characters/",
        "companies_asked": ["Amazon", "Google", "Meta", "Microsoft", "Apple"],
        "frequency_score": 0.95, "acceptance_rate": 33.8,
        "hints": ["Use a sliding window with a set.", "Expand right, shrink left when duplicate found."],
        "time_complexity": "O(n)", "space_complexity": "O(min(m,n))",
    },
    {
        "id": "3sum", "title": "3Sum", "slug": "3sum",
        "difficulty": DSADifficulty.MEDIUM, "category": "Arrays",
        "tags": ["Arrays", "Two Pointers", "Sorting"],
        "description": "Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such that i != j != k, and nums[i] + nums[j] + nums[k] == 0. Solution set must not contain duplicate triplets.",
        "constraints": ["0 <= nums.length <= 3000", "-10^5 <= nums[i] <= 10^5"],
        "inputFormat": "Array of integers.", "outputFormat": "List of unique triplets summing to zero.",
        "exampleInput": "nums = [-1,0,1,2,-1,-4]", "exampleOutput": "[[-1,-1,2],[-1,0,1]]",
        "explanation": "Sort, then use two pointers for each element.",
        "platformLink": "https://leetcode.com/problems/3sum/",
        "companies_asked": ["Amazon", "Meta", "Google", "Microsoft", "Apple"],
        "frequency_score": 0.92, "acceptance_rate": 32.0,
        "hints": ["Sort the array first.", "For each element, use two pointers on the rest."],
        "time_complexity": "O(n²)", "space_complexity": "O(n)",
    },
    {
        "id": "container-water", "title": "Container With Most Water", "slug": "container-water",
        "difficulty": DSADifficulty.MEDIUM, "category": "Arrays",
        "tags": ["Arrays", "Two Pointers", "Greedy"],
        "description": "Given integer array height of length n, find two lines that form a container holding the most water. Return the maximum amount of water.",
        "constraints": ["2 <= n <= 10^5", "0 <= height[i] <= 10^4"],
        "inputFormat": "Array of heights.", "outputFormat": "Maximum water.",
        "exampleInput": "height = [1,8,6,2,5,4,8,3,7]", "exampleOutput": "49",
        "explanation": "Two pointers from ends, always move the shorter one inward.",
        "platformLink": "https://leetcode.com/problems/container-with-most-water/",
        "companies_asked": ["Amazon", "Google", "Microsoft", "Meta"],
        "frequency_score": 0.88, "acceptance_rate": 54.0,
        "hints": ["Greedy two-pointer approach.", "Moving the taller line can only decrease area."],
        "time_complexity": "O(n)", "space_complexity": "O(1)",
    },
    {
        "id": "coin-change", "title": "Coin Change", "slug": "coin-change",
        "difficulty": DSADifficulty.MEDIUM, "category": "Dynamic Programming",
        "tags": ["Dynamic Programming", "Arrays", "Greedy"],
        "description": "Given integer array coins and integer amount, return the fewest coins needed to make up amount. Return -1 if not possible. You have infinite coins of each denomination.",
        "constraints": ["1 <= coins.length <= 12", "0 <= amount <= 10^4"],
        "inputFormat": "Array of coin denominations and target amount.", "outputFormat": "Minimum coins or -1.",
        "exampleInput": "coins = [1,2,5], amount = 11", "exampleOutput": "3",
        "explanation": "11 = 5 + 5 + 1",
        "platformLink": "https://leetcode.com/problems/coin-change/",
        "companies_asked": ["Amazon", "Google", "Apple", "Meta"],
        "frequency_score": 0.90, "acceptance_rate": 41.5,
        "hints": ["Build dp array from 0 to amount.", "dp[i] = min coins to make i."],
        "time_complexity": "O(amount × coins)", "space_complexity": "O(amount)",
    },
    {
        "id": "number-of-islands", "title": "Number of Islands", "slug": "number-of-islands",
        "difficulty": DSADifficulty.MEDIUM, "category": "Graphs",
        "tags": ["Graphs", "Depth-First Search", "Breadth-First Search"],
        "description": "Given an m×n 2D binary grid of '1's (land) and '0's (water), return the number of islands. An island is formed by connecting adjacent lands horizontally or vertically.",
        "constraints": ["1 <= m, n <= 300", "grid[i][j] is '0' or '1'."],
        "inputFormat": "2D grid of '1's and '0's.", "outputFormat": "Number of islands.",
        "exampleInput": "grid = [['1','1','0'],['0','1','0'],['0','0','1']]", "exampleOutput": "2",
        "explanation": "DFS/BFS flood-fill each island.",
        "platformLink": "https://leetcode.com/problems/number-of-islands/",
        "companies_asked": ["Amazon", "Meta", "Microsoft", "Google", "Apple"],
        "frequency_score": 0.87, "acceptance_rate": 57.5,
        "hints": ["DFS or BFS from every unvisited '1'.", "Mark visited cells as '0'."],
        "time_complexity": "O(m×n)", "space_complexity": "O(m×n)",
    },
    {
        "id": "validate-bst", "title": "Validate Binary Search Tree", "slug": "validate-bst",
        "difficulty": DSADifficulty.MEDIUM, "category": "Trees",
        "tags": ["Trees", "Depth-First Search", "Binary Search"],
        "description": "Given the root of a binary tree, determine if it is a valid BST.\n\nA valid BST requires: left subtree values < node key, right subtree values > node key, both subtrees must also be valid BSTs.",
        "constraints": ["1 <= nodes <= 10^4", "-2^31 <= Node.val <= 2^31-1"],
        "inputFormat": "Root of binary tree.", "outputFormat": "true or false.",
        "exampleInput": "root = [2,1,3]", "exampleOutput": "true",
        "explanation": "Pass min/max bounds down the recursion.",
        "platformLink": "https://leetcode.com/problems/validate-binary-search-tree/",
        "companies_asked": ["Amazon", "Meta", "Microsoft", "Bloomberg"],
        "frequency_score": 0.85, "acceptance_rate": 31.8,
        "hints": ["Pass valid range (min, max) to each node.", "Root has range (-inf, +inf)."],
        "time_complexity": "O(n)", "space_complexity": "O(n)",
    },
    {
        "id": "lru-cache", "title": "LRU Cache", "slug": "lru-cache",
        "difficulty": DSADifficulty.MEDIUM, "category": "Hash Tables",
        "tags": ["Hash Tables", "Linked List", "Design"],
        "description": "Design an LRU (Least Recently Used) cache.\n\nImplement: LRUCache(capacity), get(key) → value or -1, put(key, value) — evict LRU when capacity exceeded.",
        "constraints": ["1 <= capacity <= 3000", "At most 2×10^5 calls to get and put."],
        "inputFormat": "Operations on LRU cache.", "outputFormat": "Values for get operations.",
        "exampleInput": '["LRUCache","put","put","get"]\n[[2],[1,1],[2,2],[1]]', "exampleOutput": "[null,null,null,1]",
        "explanation": "Combine HashMap + Doubly Linked List for O(1) get and put.",
        "platformLink": "https://leetcode.com/problems/lru-cache/",
        "companies_asked": ["Amazon", "Google", "Microsoft", "Meta", "Apple"],
        "frequency_score": 0.88, "acceptance_rate": 40.6,
        "hints": ["Use OrderedDict in Python.", "Or HashMap + doubly linked list manually."],
        "time_complexity": "O(1)", "space_complexity": "O(capacity)",
    },
    {
        "id": "word-search", "title": "Word Search", "slug": "word-search",
        "difficulty": DSADifficulty.MEDIUM, "category": "Backtracking",
        "tags": ["Backtracking", "Graphs", "Depth-First Search"],
        "description": "Given an m×n grid of characters and a string word, return true if word exists in the grid.\n\nThe word can be constructed from sequentially adjacent cells (horizontally or vertically). A cell cannot be reused.",
        "constraints": ["1 <= m, n <= 6", "1 <= word.length <= 15"],
        "inputFormat": "2D grid and word string.", "outputFormat": "true or false.",
        "exampleInput": 'board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "ABCCED"', "exampleOutput": "true",
        "explanation": "DFS with backtracking — mark visited, unmark on backtrack.",
        "platformLink": "https://leetcode.com/problems/word-search/",
        "companies_asked": ["Amazon", "Microsoft", "Google", "Bloomberg"],
        "frequency_score": 0.83, "acceptance_rate": 40.7,
        "hints": ["DFS from every cell.", "Mark visited cells temporarily."],
        "time_complexity": "O(m×n×4^L)", "space_complexity": "O(L)",
    },
    {
        "id": "product-except-self", "title": "Product of Array Except Self", "slug": "product-except-self",
        "difficulty": DSADifficulty.MEDIUM, "category": "Arrays",
        "tags": ["Arrays", "Two Pointers"],
        "description": "Given integer array nums, return array answer where answer[i] is the product of all elements except nums[i]. Must run in O(n) time without division.",
        "constraints": ["2 <= nums.length <= 10^5", "-30 <= nums[i] <= 30"],
        "inputFormat": "Array of integers.", "outputFormat": "Product array.",
        "exampleInput": "nums = [1,2,3,4]", "exampleOutput": "[24,12,8,6]",
        "explanation": "Prefix product pass then suffix product pass.",
        "platformLink": "https://leetcode.com/problems/product-of-array-except-self/",
        "companies_asked": ["Amazon", "Microsoft", "Apple", "Google", "Meta"],
        "frequency_score": 0.89, "acceptance_rate": 64.4,
        "hints": ["Two passes: prefix products left-to-right, suffix products right-to-left."],
        "time_complexity": "O(n)", "space_complexity": "O(1)",
    },
    {
        "id": "spiral-matrix", "title": "Spiral Matrix", "slug": "spiral-matrix",
        "difficulty": DSADifficulty.MEDIUM, "category": "Arrays",
        "tags": ["Arrays", "Sorting", "Simulation"],
        "description": "Given an m×n matrix, return all elements in spiral order.",
        "constraints": ["1 <= m, n <= 10"],
        "inputFormat": "2D matrix.", "outputFormat": "Elements in spiral order.",
        "exampleInput": "matrix = [[1,2,3],[4,5,6],[7,8,9]]", "exampleOutput": "[1,2,3,6,9,8,7,4,5]",
        "explanation": "Maintain top, bottom, left, right boundaries and shrink after each pass.",
        "platformLink": "https://leetcode.com/problems/spiral-matrix/",
        "companies_asked": ["Microsoft", "Amazon", "Apple", "Google"],
        "frequency_score": 0.76, "acceptance_rate": 44.8,
        "hints": ["Track four boundaries and move them inward."],
        "time_complexity": "O(m×n)", "space_complexity": "O(1)",
    },
    {
        "id": "binary-tree-zigzag", "title": "Binary Tree Zigzag Level Order Traversal", "slug": "binary-tree-zigzag",
        "difficulty": DSADifficulty.MEDIUM, "category": "Trees",
        "tags": ["Trees", "Breadth-First Search", "Queue"],
        "description": "Given root of a binary tree, return the zigzag level order traversal of its nodes' values (left to right, then right to left for next level, alternating).",
        "constraints": ["0 <= nodes <= 2000", "-100 <= Node.val <= 100"],
        "inputFormat": "Root of binary tree.", "outputFormat": "Zigzag level order list of lists.",
        "exampleInput": "root = [3,9,20,null,null,15,7]", "exampleOutput": "[[3],[20,9],[15,7]]",
        "explanation": "BFS level-by-level, reverse alternate levels.",
        "platformLink": "https://leetcode.com/problems/binary-tree-zigzag-level-order-traversal/",
        "companies_asked": ["Amazon", "Bloomberg", "Meta"],
        "frequency_score": 0.77, "acceptance_rate": 56.0,
        "hints": ["Standard BFS but toggle direction each level."],
        "time_complexity": "O(n)", "space_complexity": "O(n)",
    },

    # ── HARD ───────────────────────────────────────────────────────
    {
        "id": "median-two-arrays", "title": "Median of Two Sorted Arrays", "slug": "median-two-arrays",
        "difficulty": DSADifficulty.HARD, "category": "Arrays",
        "tags": ["Arrays", "Binary Search", "Divide and Conquer"],
        "description": "Given two sorted arrays nums1 and nums2 of size m and n, return the median of the two sorted arrays. The overall run time complexity should be O(log(m+n)).",
        "constraints": ["0 <= m, n <= 1000", "1 <= m+n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        "inputFormat": "Two sorted arrays.", "outputFormat": "Median as float.",
        "exampleInput": "nums1 = [1,3], nums2 = [2]", "exampleOutput": "2.00000",
        "explanation": "Binary search on the smaller array to find the correct partition.",
        "platformLink": "https://leetcode.com/problems/median-of-two-sorted-arrays/",
        "companies_asked": ["Amazon", "Google", "Microsoft", "Apple", "Meta"],
        "frequency_score": 0.95, "acceptance_rate": 37.9,
        "hints": ["Binary search on the smaller array.", "Ensure left half total == right half total."],
        "time_complexity": "O(log(min(m,n)))", "space_complexity": "O(1)",
    },
    {
        "id": "trapping-rain-water", "title": "Trapping Rain Water", "slug": "trapping-rain-water",
        "difficulty": DSADifficulty.HARD, "category": "Arrays",
        "tags": ["Arrays", "Two Pointers", "Dynamic Programming", "Stack"],
        "description": "Given n non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.",
        "constraints": ["n == height.length", "1 <= n <= 2×10^4", "0 <= height[i] <= 10^5"],
        "inputFormat": "Array of elevations.", "outputFormat": "Total water trapped.",
        "exampleInput": "height = [0,1,0,2,1,0,1,3,2,1,2,1]", "exampleOutput": "6",
        "explanation": "Two pointer: track left_max and right_max, add min - height[i].",
        "platformLink": "https://leetcode.com/problems/trapping-rain-water/",
        "companies_asked": ["Amazon", "Google", "Microsoft", "Meta", "Apple"],
        "frequency_score": 0.92, "acceptance_rate": 60.7,
        "hints": ["Two pointers: left_max from left, right_max from right."],
        "time_complexity": "O(n)", "space_complexity": "O(1)",
    },
    {
        "id": "merge-k-lists", "title": "Merge K Sorted Lists", "slug": "merge-k-lists",
        "difficulty": DSADifficulty.HARD, "category": "Linked List",
        "tags": ["Linked List", "Divide and Conquer", "Heap"],
        "description": "You are given an array of k linked-lists, each sorted in ascending order. Merge all linked-lists into one sorted linked-list and return it.",
        "constraints": ["k == lists.length", "0 <= k <= 10^4", "-10^4 <= lists[i][j] <= 10^4"],
        "inputFormat": "Array of k sorted linked lists.", "outputFormat": "One merged sorted linked list.",
        "exampleInput": "lists = [[1,4,5],[1,3,4],[2,6]]", "exampleOutput": "[1,1,2,3,4,4,5,6]",
        "explanation": "Use min-heap of size k, always extract minimum.",
        "platformLink": "https://leetcode.com/problems/merge-k-sorted-lists/",
        "companies_asked": ["Amazon", "Google", "Meta", "Microsoft", "Apple"],
        "frequency_score": 0.90, "acceptance_rate": 49.5,
        "hints": ["Min-heap stores (val, index, node).", "Or divide and conquer merging pairs."],
        "time_complexity": "O(N log k)", "space_complexity": "O(k)",
    },
    {
        "id": "word-ladder", "title": "Word Ladder", "slug": "word-ladder",
        "difficulty": DSADifficulty.HARD, "category": "Graphs",
        "tags": ["Graphs", "Breadth-First Search", "Hash Tables", "Strings"],
        "description": "A transformation sequence from beginWord to endWord uses a dictionary wordList where each step changes exactly one letter and the new word must be in wordList.\n\nReturn the number of words in the shortest transformation sequence, or 0 if none exists.",
        "constraints": ["1 <= beginWord.length <= 10", "1 <= wordList.length <= 5000"],
        "inputFormat": "beginWord, endWord, and wordList.", "outputFormat": "Minimum transformation steps or 0.",
        "exampleInput": 'beginWord = "hit", endWord = "cog", wordList = ["hot","dot","dog","lot","log","cog"]', "exampleOutput": "5",
        "explanation": "BFS layer by layer. For each word try all one-letter mutations.",
        "platformLink": "https://leetcode.com/problems/word-ladder/",
        "companies_asked": ["Amazon", "Google", "Meta", "Microsoft"],
        "frequency_score": 0.85, "acceptance_rate": 37.6,
        "hints": ["BFS on word graph.", "For each position try all 26 letters."],
        "time_complexity": "O(M²×N)", "space_complexity": "O(M²×N)",
    },
    {
        "id": "serialize-tree", "title": "Serialize and Deserialize Binary Tree", "slug": "serialize-tree",
        "difficulty": DSADifficulty.HARD, "category": "Trees",
        "tags": ["Trees", "Depth-First Search", "Breadth-First Search", "Design"],
        "description": "Design an algorithm to serialize and deserialize a binary tree. There is no restriction on how the algorithm should work — just ensure a tree can be serialized to a string and deserialized back.",
        "constraints": ["0 <= nodes <= 10^4", "-1000 <= Node.val <= 1000"],
        "inputFormat": "Root of binary tree.", "outputFormat": "Serialized string, deserializable back.",
        "exampleInput": "root = [1,2,3,null,null,4,5]", "exampleOutput": "[1,2,3,null,null,4,5]",
        "explanation": "BFS level-order with null markers, or DFS preorder.",
        "platformLink": "https://leetcode.com/problems/serialize-and-deserialize-binary-tree/",
        "companies_asked": ["Amazon", "Meta", "Microsoft", "Google"],
        "frequency_score": 0.88, "acceptance_rate": 55.0,
        "hints": ["Use preorder DFS with 'null' for missing nodes."],
        "time_complexity": "O(n)", "space_complexity": "O(n)",
    },
    {
        "id": "regular-expression", "title": "Regular Expression Matching", "slug": "regular-expression",
        "difficulty": DSADifficulty.HARD, "category": "Dynamic Programming",
        "tags": ["Dynamic Programming", "Strings", "Recursion"],
        "description": "Implement regex matching with '.' (any single char) and '*' (zero or more of preceding). The matching must cover the entire input string.",
        "constraints": ["1 <= s.length <= 20", "1 <= p.length <= 20"],
        "inputFormat": "String s and pattern p.", "outputFormat": "true or false.",
        "exampleInput": 's = "aa", p = "a*"', "exampleOutput": "true",
        "explanation": "2D DP: dp[i][j] = s[:i] matches p[:j].",
        "platformLink": "https://leetcode.com/problems/regular-expression-matching/",
        "companies_asked": ["Google", "Meta", "Microsoft", "Amazon", "Apple"],
        "frequency_score": 0.85, "acceptance_rate": 28.2,
        "hints": ["2D DP.", "Handle '*' as: zero occurrences OR one more of preceding."],
        "time_complexity": "O(m×n)", "space_complexity": "O(m×n)",
    },
]

# ─────────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────

def get_daily_problem() -> Dict[str, Any]:
    today = date.today()
    idx = (today - date(today.year, 1, 1)).days % len(PROBLEMS)
    p = PROBLEMS[idx]
    return {
        "id": p["id"], "title": p["title"], "slug": p["slug"],
        "difficulty": p["difficulty"].value,
        "category": p["category"], "tags": p["tags"],
        "platformLink": p["platformLink"],
        "time_complexity": p.get("time_complexity", ""),
        "acceptance_rate": p.get("acceptance_rate", 0),
        "date": today.isoformat(),
    }

def filter_and_paginate(
    difficulty: Optional[str],
    topic: Optional[str],
    search: Optional[str],
    company: Optional[str],
    limit: int,
    offset: int,
    sort_by: str,
) -> Dict[str, Any]:
    result = list(PROBLEMS)

    if difficulty:
        result = [p for p in result if p["difficulty"].value == difficulty.lower()]
    if topic:
        result = [p for p in result if topic in p["tags"] or topic == p["category"]]
    if search:
        s = search.lower()
        result = [p for p in result if s in p["title"].lower() or s in p["category"].lower()
                  or any(s in t.lower() for t in p["tags"])]
    if company:
        result = [p for p in result if company in p.get("companies_asked", [])]

    # sort
    if sort_by == "frequency":
        result.sort(key=lambda x: x.get("frequency_score", 0), reverse=True)
    elif sort_by == "acceptance":
        result.sort(key=lambda x: x.get("acceptance_rate", 0), reverse=True)
    elif sort_by == "difficulty_asc":
        order = {"easy": 0, "medium": 1, "hard": 2}
        result.sort(key=lambda x: order.get(x["difficulty"].value, 1))
    elif sort_by == "difficulty_desc":
        order = {"easy": 0, "medium": 1, "hard": 2}
        result.sort(key=lambda x: order.get(x["difficulty"].value, 1), reverse=True)

    total = len(result)
    paginated = result[offset: offset + limit]

    return {
        "problems": [_serialize(p) for p in paginated],
        "total": total,
        "limit": limit,
        "offset": offset,
    }

def _serialize(p: Dict) -> Dict:
    return {
        "id": p["id"], "title": p["title"], "slug": p["slug"],
        "difficulty": p["difficulty"].value,
        "category": p["category"], "tags": p["tags"],
        "platformLink": p["platformLink"],
        "companies_asked": p.get("companies_asked", []),
        "frequency_score": p.get("frequency_score", 0),
        "acceptance_rate": p.get("acceptance_rate", 0),
        "time_complexity": p.get("time_complexity", ""),
        "space_complexity": p.get("space_complexity", ""),
    }

def _serialize_full(p: Dict) -> Dict:
    d = _serialize(p)
    d.update({
        "description": p.get("description", ""),
        "constraints": p.get("constraints", []),
        "inputFormat": p.get("inputFormat", ""),
        "outputFormat": p.get("outputFormat", ""),
        "exampleInput": p.get("exampleInput", ""),
        "exampleOutput": p.get("exampleOutput", ""),
        "explanation": p.get("explanation", ""),
        "hints": p.get("hints", []),
    })
    return d

# ─────────────────────────────────────────────
#  FASTAPI APP
# ─────────────────────────────────────────────

app = FastAPI(title="DSA Practice Service", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/problems")
async def list_problems(
    difficulty: Optional[str] = None,
    topic:      Optional[str] = None,
    search:     Optional[str] = None,
    company:    Optional[str] = None,
    sort_by:    str           = Query("frequency", enum=["frequency","acceptance","difficulty_asc","difficulty_desc"]),
    limit:      int           = Query(20, ge=1, le=100),
    offset:     int           = Query(0, ge=0),
):
    return filter_and_paginate(difficulty, topic, search, company, limit, offset, sort_by)

@app.get("/api/problems/{slug}")
async def get_problem(slug: str):
    p = next((x for x in PROBLEMS if x["slug"] == slug), None)
    if not p:
        from fastapi import HTTPException
        raise HTTPException(404, "Problem not found")
    return _serialize_full(p)

@app.get("/api/daily-problem")
async def daily_problem():
    return get_daily_problem()

@app.get("/api/topics")
async def get_topics():
    return {"topics": TOPICS}

@app.get("/api/difficulties")
async def get_difficulties():
    easy   = sum(1 for p in PROBLEMS if p["difficulty"] == DSADifficulty.EASY)
    medium = sum(1 for p in PROBLEMS if p["difficulty"] == DSADifficulty.MEDIUM)
    hard   = sum(1 for p in PROBLEMS if p["difficulty"] == DSADifficulty.HARD)
    return {"difficulties": [
        {"value": "easy",   "label": "Easy",   "count": easy},
        {"value": "medium", "label": "Medium", "count": medium},
        {"value": "hard",   "label": "Hard",   "count": hard},
    ]}

@app.get("/api/companies")
async def get_companies():
    seen, companies = set(), []
    for p in PROBLEMS:
        for c in p.get("companies_asked", []):
            if c not in seen:
                seen.add(c); companies.append(c)
    return {"companies": sorted(companies)}

@app.get("/api/stats")
async def get_stats():
    return {
        "total": len(PROBLEMS),
        "easy":   sum(1 for p in PROBLEMS if p["difficulty"] == DSADifficulty.EASY),
        "medium": sum(1 for p in PROBLEMS if p["difficulty"] == DSADifficulty.MEDIUM),
        "hard":   sum(1 for p in PROBLEMS if p["difficulty"] == DSADifficulty.HARD),
        "topics": len(TOPICS),
        "companies": len({c for p in PROBLEMS for c in p.get("companies_asked", [])}),
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "dsa-practice", "problems": len(PROBLEMS)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004, reload=True)