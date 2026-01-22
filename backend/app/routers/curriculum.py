"""
Curriculum router - Institution curriculum analysis and alignment
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import io
import PyPDF2

from app.database import get_db
from app.models import Curriculum, Skill
from app.schemas import CurriculumCreate, CurriculumResponse
# Authentication removed for now
from app.services.ai_service import AIService
from app.services.trends_service import TrendsService

router = APIRouter()
trends_service = TrendsService()

# Lazy initialization of AI service
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

@router.post("/upload", response_model=CurriculumResponse)
async def upload_curriculum(
    name: str,
    program: str = None,
    file: UploadFile = File(None),
    curriculum_text: str = None,
    db: Session = Depends(get_db)
):
    """Upload curriculum for analysis"""
    
    # Get curriculum text
    if file:
        file_content = await file.read()
        if file.filename.endswith('.pdf'):
            text = extract_text_from_pdf(file_content)
        else:
            text = file_content.decode('utf-8')
    elif curriculum_text:
        text = curriculum_text
    else:
        raise HTTPException(status_code=400, detail="Either file or curriculum_text must be provided")
    
    # Extract skills from curriculum
    ai_service = get_ai_service()
    extracted_skills = ai_service.extract_skills_from_curriculum(text)
    
    # Get industry and future skills for comparison
    industry_skills = db.query(Skill).filter(
        Skill.trend_status.in_(["high-growth", "saturated"])
    ).limit(30).all()
    industry_skill_names = [s.name for s in industry_skills]
    
    future_skills = db.query(Skill).filter(
        Skill.trend_status.in_(["emerging", "high-growth"])
    ).limit(20).all()
    future_skill_names = [s.name for s in future_skills]
    
    # Generate recommendations
    ai_service = get_ai_service()
    recommendations = ai_service.generate_curriculum_recommendations(
        current_curriculum_skills=extracted_skills,
        industry_skills=industry_skill_names,
        future_skills=future_skill_names
    )
    
    # Create curriculum record (using default user_id for now)
    default_user_id = 1
    curriculum = Curriculum(
        institution_id=default_user_id,
        name=name,
        program=program,
        curriculum_text=text,
        extracted_skills=extracted_skills,
        alignment_score=recommendations.get("alignment_score", 0.0),
        recommendations=recommendations
    )
    db.add(curriculum)
    db.commit()
    db.refresh(curriculum)
    
    return curriculum

@router.get("/", response_model=List[CurriculumResponse])
async def get_institution_curricula(
    db: Session = Depends(get_db)
):
    """Get all curricula"""
    default_user_id = 1
    curricula = db.query(Curriculum).filter(Curriculum.institution_id == default_user_id).all()
    return curricula

@router.get("/{curriculum_id}", response_model=CurriculumResponse)
async def get_curriculum(
    curriculum_id: int,
    db: Session = Depends(get_db)
):
    """Get specific curriculum by ID"""
    default_user_id = 1
    curriculum = db.query(Curriculum).filter(
        Curriculum.id == curriculum_id,
        Curriculum.institution_id == default_user_id
    ).first()
    
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    
    return curriculum

@router.post("/{curriculum_id}/analyze")
async def analyze_curriculum(
    curriculum_id: int,
    db: Session = Depends(get_db)
):
    """Re-analyze curriculum with latest market data"""
    default_user_id = 1
    curriculum = db.query(Curriculum).filter(
        Curriculum.id == curriculum_id,
        Curriculum.institution_id == default_user_id
    ).first()
    
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    
    # Get latest industry and future skills
    industry_skills = db.query(Skill).filter(
        Skill.trend_status.in_(["high-growth", "saturated"])
    ).limit(30).all()
    industry_skill_names = [s.name for s in industry_skills]
    
    future_skills = db.query(Skill).filter(
        Skill.trend_status.in_(["emerging", "high-growth"])
    ).limit(20).all()
    future_skill_names = [s.name for s in future_skills]
    
    # Regenerate recommendations
    ai_service = get_ai_service()
    recommendations = ai_service.generate_curriculum_recommendations(
        current_curriculum_skills=curriculum.extracted_skills or [],
        industry_skills=industry_skill_names,
        future_skills=future_skill_names
    )
    
    # Update curriculum
    curriculum.alignment_score = recommendations.get("alignment_score", 0.0)
    curriculum.recommendations = recommendations
    db.commit()
    db.refresh(curriculum)
    
    return curriculum
