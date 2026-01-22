"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# Auth Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    user_type: str  # 'student' or 'institution'

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Skill Schemas
class SkillBase(BaseModel):
    name: str
    category: Optional[str] = None
    domain: Optional[str] = None
    description: Optional[str] = None

class SkillCreate(SkillBase):
    pass

class SkillResponse(SkillBase):
    id: int
    current_demand_score: float
    future_demand_score: float
    trend_status: Optional[str]
    forecast_6m: Optional[float]
    forecast_1y: Optional[float]
    forecast_3y: Optional[float]
    
    class Config:
        from_attributes = True

# Profile Schemas
class ProfileCreate(BaseModel):
    domain: Optional[str] = None
    target_role: Optional[str] = None
    experience_level: Optional[str] = None

class ProfileResponse(BaseModel):
    id: int
    user_id: int
    domain: Optional[str]
    current_skills: Optional[List[str]]
    target_role: Optional[str]
    experience_level: Optional[str]
    
    class Config:
        from_attributes = True

# Skill Gap Schemas
class SkillGapResponse(BaseModel):
    skill_id: int
    skill_name: str
    gap_score: float
    priority: str
    timeframe: str
    current_demand_score: float
    future_demand_score: float
    
    class Config:
        from_attributes = True

class SkillGapAnalysisResponse(BaseModel):
    profile_id: int
    overall_gap_score: float
    skill_gaps: List[SkillGapResponse]
    priority_skills_short_term: List[str]
    priority_skills_long_term: List[str]

# Roadmap Schemas
class RoadmapStep(BaseModel):
    step_number: int
    skill: str
    prerequisites: List[str]
    estimated_time_weeks: int
    suggested_courses: List[str]
    suggested_certifications: List[str]
    mini_projects: List[str]

class RoadmapCreate(BaseModel):
    target_role: str
    target_timeline_months: int
    domain: Optional[str] = None

class RoadmapResponse(BaseModel):
    id: int
    title: str
    target_role: str
    target_timeline_months: int
    roadmap_data: Dict[str, Any]
    generated_at: datetime
    
    class Config:
        from_attributes = True

# Curriculum Schemas
class CurriculumCreate(BaseModel):
    name: str
    program: Optional[str] = None

class CurriculumResponse(BaseModel):
    id: int
    institution_id: int
    name: str
    program: Optional[str]
    extracted_skills: Optional[List[str]]
    alignment_score: Optional[float]
    recommendations: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True

# Analytics Schemas
class SkillForecastResponse(BaseModel):
    skill_name: str
    current_demand: float
    forecast_6m: float
    forecast_1y: float
    forecast_3y: float
    trend_status: str
    google_trends_score: float

class TrendAnalysisResponse(BaseModel):
    skill: str
    trend_data: List[Dict[str, Any]]
    growth_rate: float
    classification: str  # emerging, high-growth, saturated, declining
