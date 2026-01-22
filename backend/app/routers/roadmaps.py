"""
Roadmaps router - Personalized learning roadmap generation
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import UserProfile, Roadmap
from app.schemas import RoadmapCreate, RoadmapResponse
# Authentication removed for now
from app.services.ai_service import AIService

router = APIRouter()

# Lazy initialization of AI service
_ai_service = None

def get_ai_service():
    """Get or create AI service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service

@router.post("/generate", response_model=RoadmapResponse)
async def generate_roadmap(
    roadmap_data: RoadmapCreate,
    db: Session = Depends(get_db)
):
    """Generate personalized learning roadmap"""
    # Get user profile (using default user_id for now)
    default_user_id = 1
    profile = db.query(UserProfile).filter(UserProfile.user_id == default_user_id).first()
    current_skills = profile.current_skills if profile else []
    
    # Generate roadmap using AI
    ai_service = get_ai_service()
    roadmap_content = ai_service.generate_skill_roadmap(
        current_skills=current_skills,
        target_role=roadmap_data.target_role,
        timeline_months=roadmap_data.target_timeline_months,
        domain=roadmap_data.domain
    )
    
    # Save roadmap
    roadmap = Roadmap(
        user_id=default_user_id,
        title=roadmap_content.get("title", f"Roadmap to {roadmap_data.target_role}"),
        target_role=roadmap_data.target_role,
        target_timeline_months=roadmap_data.target_timeline_months,
        roadmap_data=roadmap_content
    )
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)
    
    return roadmap

@router.get("/", response_model=List[RoadmapResponse])
async def get_user_roadmaps(
    db: Session = Depends(get_db)
):
    """Get all roadmaps"""
    default_user_id = 1
    roadmaps = db.query(Roadmap).filter(Roadmap.user_id == default_user_id).all()
    return roadmaps

@router.get("/{roadmap_id}", response_model=RoadmapResponse)
async def get_roadmap(
    roadmap_id: int,
    db: Session = Depends(get_db)
):
    """Get specific roadmap by ID"""
    default_user_id = 1
    roadmap = db.query(Roadmap).filter(
        Roadmap.id == roadmap_id,
        Roadmap.user_id == default_user_id
    ).first()
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    return roadmap
