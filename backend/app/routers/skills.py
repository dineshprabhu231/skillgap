"""
Skills router - Skill gap analysis and skill management
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import PyPDF2
import io

from app.database import get_db
from app.models import UserProfile, Skill, SkillGap
from app.schemas import (
    ProfileCreate, ProfileResponse, SkillGapAnalysisResponse,
    SkillGapResponse, SkillResponse
)
# Authentication removed for now
from app.services.ai_service import AIService
from app.services.trends_service import TrendsService

router = APIRouter()
trends_service = TrendsService()

# Lazy initialization of AI service to avoid errors if .env is not loaded yet
_ai_service = None

def get_ai_service():
    """Get or create AI service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

@router.post("/upload-resume", response_model=ProfileResponse)
async def upload_resume(
    file: UploadFile = File(...),
    domain: str = None,
    target_role: str = None,
    db: Session = Depends(get_db)
):
    """Upload resume and extract skills"""
    
    # Read file content
    file_content = await file.read()
    
    # Extract text
    if file.filename.endswith('.pdf'):
        resume_text = extract_text_from_pdf(file_content)
    else:
        resume_text = file_content.decode('utf-8')
    
    # Extract skills using AI
    ai_service = get_ai_service()
    extracted_skills = ai_service.extract_skills_from_resume(resume_text)
    
    # Get or create user profile (using default user_id since auth is disabled)
    default_user_id = 1
    profile = db.query(UserProfile).filter(UserProfile.user_id == default_user_id).first()
    if not profile:
        profile = UserProfile(
            user_id=default_user_id,
            resume_text=resume_text,
            domain=domain,
            target_role=target_role,
            current_skills=extracted_skills
        )
        db.add(profile)
    else:
        profile.resume_text = resume_text
        profile.domain = domain
        profile.target_role = target_role
        profile.current_skills = extracted_skills
    
    db.commit()
    db.refresh(profile)
    
    return profile

@router.post("/analyze-gaps", response_model=SkillGapAnalysisResponse)
async def analyze_skill_gaps(
    db: Session = Depends(get_db)
):
    """Analyze skill gaps"""
    default_user_id = 1
    profile = db.query(UserProfile).filter(UserProfile.user_id == default_user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Please upload a resume first.")
    
    current_skills = profile.current_skills or []
    
    # Get trending skills for the domain
    domain_skills = []
    if profile.domain:
        domain_skills = db.query(Skill).filter(Skill.domain == profile.domain).all()
    
    if not domain_skills:
        # If no domain skills, get all high-demand skills
        domain_skills = db.query(Skill).filter(Skill.trend_status.in_(["emerging", "high-growth"])).limit(20).all()
    
    if not domain_skills:
        # If still no skills, get any skills
        domain_skills = db.query(Skill).limit(20).all()
    
    required_skills = [skill.name for skill in domain_skills]
    
    # If no skills in database at all, return a helpful message
    if not required_skills:
        return SkillGapAnalysisResponse(
            profile_id=profile.id,
            overall_gap_score=0.0,
            skill_gaps=[],
            priority_skills_short_term=[],
            priority_skills_long_term=[]
        )
    
    # Use AI to analyze gaps
    ai_service = get_ai_service()
    gap_analysis = ai_service.analyze_skill_gaps(
        current_skills,
        required_skills,
        profile.target_role or "Professional"
    )
    
    # Calculate overall gap score
    overall_gap_score = gap_analysis.get("gap_score", 0.0)
    
    # Create skill gap records
    skill_gaps = []
    for skill_name in gap_analysis.get("missing_skills", []):
        skill = db.query(Skill).filter(Skill.name == skill_name).first()
        if skill:
            # Determine priority and timeframe
            priority = "high" if skill_name in gap_analysis.get("priority_skills_short_term", []) else "medium"
            timeframe = "short-term" if skill_name in gap_analysis.get("priority_skills_short_term", []) else "long-term"
            
            gap = SkillGap(
                profile_id=profile.id,
                skill_id=skill.id,
                gap_score=1.0,  # Missing skill = full gap
                priority=priority,
                timeframe=timeframe
            )
            skill_gaps.append(gap)
    
    # Clear existing gaps and add new ones
    db.query(SkillGap).filter(SkillGap.profile_id == profile.id).delete()
    db.add_all(skill_gaps)
    db.commit()
    
    # Build response
    gap_responses = []
    for gap in skill_gaps:
        skill = db.query(Skill).filter(Skill.id == gap.skill_id).first()
        gap_responses.append(SkillGapResponse(
            skill_id=skill.id,
            skill_name=skill.name,
            gap_score=gap.gap_score,
            priority=gap.priority,
            timeframe=gap.timeframe,
            current_demand_score=skill.current_demand_score,
            future_demand_score=skill.future_demand_score
        ))
    
    return SkillGapAnalysisResponse(
        profile_id=profile.id,
        overall_gap_score=overall_gap_score,
        skill_gaps=gap_responses,
        priority_skills_short_term=gap_analysis.get("priority_skills_short_term", []),
        priority_skills_long_term=gap_analysis.get("priority_skills_long_term", [])
    )

@router.get("/trending", response_model=List[SkillResponse])
async def get_trending_skills(
    domain: str = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get trending skills based on demand and forecasts"""
    query = db.query(Skill)
    if domain:
        query = query.filter(Skill.domain == domain)
    
    skills = query.order_by(Skill.future_demand_score.desc()).limit(limit).all()
    return skills

@router.get("/forecast/{skill_name}")
async def get_skill_forecast(
    skill_name: str,
    db: Session = Depends(get_db)
):
    """Get detailed forecast for a specific skill"""
    skill = db.query(Skill).filter(Skill.name == skill_name).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    # Get trend data
    trend_data = trends_service.get_trend_data([skill_name])
    skill_trend = trend_data.get(skill_name, {})
    
    return {
        "skill": skill_name,
        "current_demand": skill.current_demand_score,
        "future_demand": skill.future_demand_score,
        "trend_status": skill.trend_status,
        "forecast_6m": skill.forecast_6m,
        "forecast_1y": skill.forecast_1y,
        "forecast_3y": skill.forecast_3y,
        "google_trends_score": skill.google_trends_score,
        "growth_rate": skill_trend.get("growth_rate", 0.0),
        "trend_data": skill_trend.get("trend_data", {})
    }
