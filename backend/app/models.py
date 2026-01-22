"""
Database models for SGIP
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    user_type = Column(String, nullable=False)  # 'student', 'institution', 'admin'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    profiles = relationship("UserProfile", back_populates="user", cascade="all, delete-orphan")
    roadmaps = relationship("Roadmap", back_populates="user", cascade="all, delete-orphan")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_text = Column(Text)
    resume_file_path = Column(String)
    domain = Column(String)  # AI, Healthcare, FinTech, etc.
    current_skills = Column(JSON)  # List of skills
    target_role = Column(String)
    experience_level = Column(String)  # fresher, junior, mid, senior
    
    # Relationships
    user = relationship("User", back_populates="profiles")
    skill_gaps = relationship("SkillGap", back_populates="profile", cascade="all, delete-orphan")

class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String)  # Technical, Soft, Domain-specific
    domain = Column(String)  # AI, Healthcare, FinTech, etc.
    description = Column(Text)
    
    # Trend data
    current_demand_score = Column(Float, default=0.0)
    future_demand_score = Column(Float, default=0.0)
    trend_status = Column(String)  # emerging, high-growth, saturated, declining
    google_trends_score = Column(Float, default=0.0)
    
    # Forecasts
    forecast_6m = Column(Float)
    forecast_1y = Column(Float)
    forecast_3y = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SkillGap(Base):
    __tablename__ = "skill_gaps"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    gap_score = Column(Float)  # 0-1, higher = bigger gap
    priority = Column(String)  # high, medium, low
    timeframe = Column(String)  # short-term, long-term
    
    # Relationships
    profile = relationship("UserProfile", back_populates="skill_gaps")
    skill = relationship("Skill")

class Roadmap(Base):
    __tablename__ = "roadmaps"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    target_role = Column(String)
    target_timeline_months = Column(Integer)
    roadmap_data = Column(JSON)  # Full roadmap structure
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="roadmaps")

class Curriculum(Base):
    __tablename__ = "curricula"
    
    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    program = Column(String)  # B.Tech, M.Tech, etc.
    curriculum_text = Column(Text)
    curriculum_file_path = Column(String)
    extracted_skills = Column(JSON)
    alignment_score = Column(Float)  # 0-1, how aligned with industry
    recommendations = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SkillTrend(Base):
    __tablename__ = "skill_trends"
    
    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    search_volume = Column(Float)
    job_postings_count = Column(Integer)
    demand_score = Column(Float)
    
    skill = relationship("Skill")
