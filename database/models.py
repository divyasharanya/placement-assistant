"""
Database models for the AI Mock Interview Trainer
Based on the system design schema
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Float, ForeignKey, Enum as SQLEnum, JSON, ARRAY, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY as PGArray
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class UserRole(str, Enum):
    CANDIDATE = "candidate"
    ADMIN = "admin"
    RECRUITER = "recruiter"


class SubscriptionTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class ExperienceLevel(str, Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    STAFF = "staff"
    PRINCIPAL = "principal"


class ResumeSourceType(str, Enum):
    PDF = "pdf"
    LINKEDIN = "linkedin"
    GITHUB = "github"
    LEETCODE = "leetcode"
    MANUAL = "manual"


class InterviewType(str, Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SYSTEM_DESIGN = "system_design"
    DSA = "dsa"
    MIXED = "mixed"


class InterviewDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class InterviewStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ABANDONED = "abandoned"


class InterviewMode(str, Enum):
    TEXT = "text"
    VOICE = "voice"
    HYBRID = "hybrid"


class DSADifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class SubmissionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    RUNTIME_ERROR = "runtime_error"
    COMPILATION_ERROR = "compilation_error"


class SkillCategory(str, Enum):
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    TOOL = "tool"
    SOFT_SKILL = "soft_skill"
    DOMAIN = "domain"


class ProficiencyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


# ==================== SQLAlchemy Models ====================


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    avatar_url = Column(Text)
    role = Column(SQLEnum(UserRole), default=UserRole.CANDIDATE)
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    email_verified = Column(Boolean, default=False)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255))
    last_login_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    resumes = relationship("Resume", back_populates="user")
    resume_analyses = relationship("ResumeAnalysis", back_populates="user")
    interview_sessions = relationship("InterviewSession", back_populates="user")
    dsa_submissions = relationship("DSASubmission", back_populates="user")
    skill_assessments = relationship("SkillAssessment", back_populates="user")
    learning_paths = relationship("LearningPath", back_populates="user")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    target_role = Column(String(255))
    experience_level = Column(SQLEnum(ExperienceLevel))
    preferred_languages = Column(PGArray(String))
    timezone = Column(String(50))
    interview_frequency = Column(Integer, default=3)
    learning_goals = Column(JSON)
    notification_preferences = Column(JSON, default={
        "email_daily_digest": True,
        "push_interview_reminders": True,
        "weekly_progress": True
    })

    user = relationship("User", back_populates="profile")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    source_type = Column(SQLEnum(ResumeSourceType), nullable=False)
    source_url = Column(Text)
    raw_content = Column(Text)
    parsed_data = Column(JSON)
    ats_score = Column(Float)
    improvement_suggestions = Column(JSON)
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="resumes")
    sections = relationship("ResumeSection", back_populates="resume")
    skills = relationship("ResumeSkill", back_populates="resume")


class ResumeSection(Base):
    __tablename__ = "resume_sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), index=True)
    section_type = Column(String(50), nullable=False)
    content = Column(JSON, nullable=False)
    ai_extracted = Column(Boolean, default=True)
    confidence_score = Column(Float)
    display_order = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    resume = relationship("Resume", back_populates="sections")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    category = Column(SQLEnum(SkillCategory), nullable=False)
    aliases = Column(PGArray(String))
    difficulty_level = Column(Integer, check_constraint="difficulty_level BETWEEN 1 AND 10")
    related_skills = Column(PGArray(UUID(as_uuid=True)))
    demand_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class ResumeSkill(Base):
    __tablename__ = "resume_skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), index=True)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"))
    proficiency_level = Column(SQLEnum(ProficiencyLevel))
    years_experience = Column(Float)
    is_primary = Column(Boolean, default=False)
    extracted_from = Column(String(20), default="resume")

    resume = relationship("Resume", back_populates="skills")
    skill = relationship("Skill")


class ResumeAnalysis(Base):
    """Store resume analysis results for user history tracking"""
    __tablename__ = "resume_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    file_name = Column(String(255), nullable=False)
    ats_score = Column(Float, nullable=False)
    skills_detected = Column(PGArray(String), default=[])
    missing_skills = Column(PGArray(String), default=[])
    strengths = Column(PGArray(String), default=[])
    improvements = Column(PGArray(String), default=[])
    suggestions = Column(PGArray(String), default=[])
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to user
    user = relationship("User", back_populates="resumes")


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"))
    type = Column(SQLEnum(InterviewType), nullable=False)
    difficulty_level = Column(SQLEnum(InterviewDifficulty), nullable=False)
    status = Column(SQLEnum(InterviewStatus), default=InterviewStatus.SCHEDULED)
    mode = Column(SQLEnum(InterviewMode), default=InterviewMode.TEXT)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    duration_seconds = Column(Integer)
    configuration = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="interview_sessions")
    questions = relationship("InterviewQuestion", back_populates="session")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id"), index=True)
    question_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    expected_answer_points = Column(JSON)
    difficulty_level = Column(Integer, check_constraint="difficulty_level BETWEEN 1 AND 10")
    topic_tags = Column(PGArray(UUID(as_uuid=True)))
    sequence_order = Column(Integer, nullable=False)
    time_limit_seconds = Column(Integer)
    hints = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("InterviewSession", back_populates="questions")
    responses = relationship("InterviewResponse", back_populates="question")


class InterviewResponse(Base):
    __tablename__ = "interview_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("interview_questions.id"), index=True)
    response_type = Column(String(20), nullable=False)
    content = Column(Text)
    audio_url = Column(Text)
    code_submission = Column(Text)
    language_used = Column(String(50))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    thinking_time_seconds = Column(Integer)
    word_count = Column(Integer)
    confidence_metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    question = relationship("InterviewQuestion", back_populates="responses")
    analysis = relationship("ResponseAnalysis", back_populates="response", uselist=False)


class ResponseAnalysis(Base):
    __tablename__ = "response_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    response_id = Column(UUID(as_uuid=True), ForeignKey("interview_responses.id"), unique=True)
    technical_accuracy_score = Column(Float)
    communication_score = Column(Float)
    problem_solving_score = Column(Float)
    explanation_clarity_score = Column(Float)
    confidence_score = Column(Float)
    overall_score = Column(Float)
    strengths = Column(PGArray(String))
    weaknesses = Column(PGArray(String))
    improvement_suggestions = Column(JSON)
    ai_model_version = Column(String(50))
    processing_time_ms = Column(Integer)
    raw_analysis = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    response = relationship("InterviewResponse", back_populates="analysis")


class DSAProblem(Base):
    __tablename__ = "dsa_problems"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    difficulty = Column(SQLEnum(DSADifficulty), nullable=False)
    topics = Column(PGArray(UUID(as_uuid=True)))
    companies_asked = Column(PGArray(String))
    frequency_score = Column(Float)
    time_complexity_expected = Column(String(50))
    space_complexity_expected = Column(String(50))
    hints = Column(JSON)
    editorial = Column(Text)
    solution_code = Column(JSON)
    test_cases = Column(JSON, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DSASubmission(Base):
    __tablename__ = "dsa_submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("dsa_problems.id"), index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id"))
    code = Column(Text, nullable=False)
    language = Column(String(50), nullable=False)
    status = Column(SQLEnum(SubmissionStatus), default=SubmissionStatus.PENDING)
    runtime_ms = Column(Integer)
    memory_mb = Column(Float)
    test_cases_passed = Column(Integer)
    total_test_cases = Column(Integer)
    failed_test_case = Column(JSON)
    time_spent_seconds = Column(Integer)
    attempts_count = Column(Integer, default=1)
    plagiarism_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="dsa_submissions")
    problem = relationship("DSAProblem")


class SkillAssessment(Base):
    __tablename__ = "skill_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"))
    current_level = Column(Float)
    confidence_interval = Column(Float)
    last_assessed_at = Column(DateTime)
    assessment_history = Column(PGArray(JSON))
    weak_subtopics = Column(PGArray(String))
    strong_subtopics = Column(PGArray(String))

    user = relationship("User", back_populates="skill_assessments")
    skill = relationship("Skill")


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    target_skills = Column(PGArray(UUID(as_uuid=True)))
    estimated_duration_hours = Column(Integer)
    current_progress = Column(Float, default=0)
    status = Column(String(20), default="active")
    milestones = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="learning_paths")


# ==================== Pydantic Schemas ====================


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    avatar_url: Optional[str]
    role: UserRole
    subscription_tier: SubscriptionTier
    email_verified: bool

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    target_role: Optional[str] = None
    experience_level: Optional[ExperienceLevel] = None
    preferred_languages: Optional[List[str]] = None
    timezone: Optional[str] = None
    interview_frequency: Optional[int] = None
    learning_goals: Optional[Dict[str, Any]] = None
    notification_preferences: Optional[Dict[str, Any]] = None


class ResumeCreate(BaseModel):
    source_type: ResumeSourceType
    source_url: Optional[str] = None
    raw_content: Optional[str] = None


class ResumeResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    source_type: ResumeSourceType
    parsed_data: Optional[Dict[str, Any]]
    ats_score: Optional[float]
    version: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class InterviewSessionCreate(BaseModel):
    resume_id: Optional[uuid.UUID] = None
    type: InterviewType
    difficulty_level: InterviewDifficulty
    mode: InterviewMode = InterviewMode.TEXT
    configuration: Optional[Dict[str, Any]] = None


class InterviewSessionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    resume_id: Optional[uuid.UUID]
    type: InterviewType
    difficulty_level: InterviewDifficulty
    status: InterviewStatus
    mode: InterviewMode
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    duration_seconds: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class InterviewQuestionResponse(BaseModel):
    id: uuid.UUID
    question_type: str
    content: str
    expected_answer_points: Optional[List[str]]
    difficulty_level: int
    sequence_order: int
    time_limit_seconds: Optional[int]
    hints: Optional[List[str]]

    class Config:
        from_attributes = True


class AnswerSubmission(BaseModel):
    content: Optional[str] = None
    audio_url: Optional[str] = None
    code_submission: Optional[str] = None
    language_used: Optional[str] = None


class ResponseAnalysisResponse(BaseModel):
    id: uuid.UUID
    technical_accuracy_score: Optional[float]
    communication_score: Optional[float]
    problem_solving_score: Optional[float]
    explanation_clarity_score: Optional[float]
    confidence_score: Optional[float]
    overall_score: Optional[float]
    strengths: Optional[List[str]]
    weaknesses: Optional[List[str]]
    improvement_suggestions: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class DSAProblemResponse(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    description: str
    difficulty: DSADifficulty
    topics: Optional[List[str]]
    companies_asked: Optional[List[str]]
    time_complexity_expected: Optional[str]
    space_complexity_expected: Optional[str]
    hints: Optional[List[str]]
    is_premium: bool

    class Config:
        from_attributes = True


class DSASubmissionCreate(BaseModel):
    problem_id: uuid.UUID
    code: str
    language: str


class DSASubmissionResponse(BaseModel):
    id: uuid.UUID
    status: SubmissionStatus
    runtime_ms: Optional[int]
    memory_mb: Optional[float]
    test_cases_passed: Optional[int]
    total_test_cases: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
