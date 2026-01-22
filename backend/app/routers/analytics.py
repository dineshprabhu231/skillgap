"""
Analytics router - Dashboards and visual insights
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from sqlalchemy import func

from app.database import get_db
from app.models import Skill, SkillTrend, UserProfile, Curriculum, SkillGap
from app.schemas import SkillForecastResponse, TrendAnalysisResponse
# Authentication removed for now
from app.services.trends_service import TrendsService

router = APIRouter()
trends_service = TrendsService()

@router.get("/skill-heatmap")
async def get_skill_heatmap(
    domain: str = None,
    db: Session = Depends(get_db)
):
    """Get skill heatmap data for visualization"""
    query = db.query(Skill)
    if domain:
        query = query.filter(Skill.domain == domain)
    
    skills = query.all()
    
    heatmap_data = []
    for skill in skills:
        heatmap_data.append({
            "skill": skill.name,
            "domain": skill.domain,
            "current_demand": skill.current_demand_score,
            "future_demand": skill.future_demand_score,
            "trend_status": skill.trend_status,
            "category": skill.category
        })
    
    return {"skills": heatmap_data}

@router.get("/demand-vs-supply")
async def get_demand_vs_supply(
    domain: str = None,
    db: Session = Depends(get_db)
):
    """Get demand vs supply analysis"""
    # Get skills with demand scores
    query = db.query(Skill)
    if domain:
        query = query.filter(Skill.domain == domain)
    
    skills = query.all()
    
    # Count users with each skill (supply) - simplified for SQLite compatibility
    demand_supply_data = []
    for skill in skills:
        # Count profiles - simplified count
        supply_count = db.query(UserProfile).count()
        
        demand_supply_data.append({
            "skill": skill.name,
            "demand_score": skill.current_demand_score or 0,
            "future_demand_score": skill.future_demand_score or 0,
            "supply_count": supply_count,
            "gap": (skill.current_demand_score or 0) - (supply_count / 10)  # Normalized
        })
    
    return {"data": demand_supply_data}

@router.get("/trend-growth")
async def get_trend_growth(
    skill_names: str = None,  # Comma-separated
    db: Session = Depends(get_db)
):
    """Get trend growth charts data"""
    if not skill_names:
        # Get top trending skills from database
        skills = db.query(Skill).filter(
            Skill.trend_status.in_(["emerging", "high-growth"])
        ).limit(10).all()
        skill_list = [s.name for s in skills]
    else:
        skill_list = [s.strip() for s in skill_names.split(",")]
    
    if not skill_list:
        return {"trends": []}
    
    # Get trend data - use database data instead of live Google Trends for speed
    results = []
    for skill_name in skill_list:
        skill = db.query(Skill).filter(Skill.name == skill_name).first()
        if skill:
            # Generate mock trend data based on database values
            trend_data = []
            base_value = skill.current_demand_score or 50
            for i in range(12):
                trend_data.append({
                    "date": f"2025-{i+1:02d}-01",
                    "value": base_value + (i * ((skill.future_demand_score or base_value) - base_value) / 12)
                })
            
            results.append(TrendAnalysisResponse(
                skill=skill_name,
                trend_data=trend_data,
                growth_rate=((skill.future_demand_score or 0) - (skill.current_demand_score or 0)) / max(skill.current_demand_score or 1, 1) * 100,
                classification=skill.trend_status or "saturated"
            ))
    
    return {"trends": results}

@router.get("/employability-readiness")
async def get_employability_readiness(
    db: Session = Depends(get_db)
):
    """Get employability readiness index"""
    default_user_id = 1
    profile = db.query(UserProfile).filter(UserProfile.user_id == default_user_id).first()
    if not profile:
        return {"readiness_score": 0.0, "message": "Please upload a resume first"}
    
    # Calculate readiness based on skill gaps
    skill_gaps = db.query(SkillGap).filter(SkillGap.profile_id == profile.id).all()
    
    if not skill_gaps:
        return {"readiness_score": 0.0, "message": "Please run skill gap analysis first"}
    
    # Calculate average gap (inverse of readiness)
    avg_gap = sum([gap.gap_score for gap in skill_gaps]) / len(skill_gaps) if skill_gaps else 1.0
    readiness_score = (1.0 - avg_gap) * 100
    
    # Get domain-specific readiness
    domain_skills = db.query(Skill).filter(Skill.domain == profile.domain).all()
    domain_skill_names = [s.name for s in domain_skills]
    current_skills = profile.current_skills or []
    
    domain_coverage = len(set(current_skills) & set(domain_skill_names)) / len(domain_skill_names) if domain_skill_names else 0.0
    
    return {
        "readiness_score": readiness_score,
        "domain_coverage": domain_coverage * 100,
        "total_skills_required": len(domain_skill_names),
        "skills_covered": len(set(current_skills) & set(domain_skill_names)),
        "priority_gaps": len([g for g in skill_gaps if g.priority == "high"])
    }

@router.get("/institution-readiness")
async def get_institution_readiness(
    db: Session = Depends(get_db)
):
    """Get readiness scores for institution"""
    default_user_id = 1
    curricula = db.query(Curriculum).filter(Curriculum.institution_id == default_user_id).all()
    
    if not curricula:
        return {
            "placement_readiness": 0.0,
            "industry_collaboration": 0.0,
            "accreditation": 0.0,
            "message": "Please upload curricula first"
        }
    
    # Aggregate readiness scores
    total_readiness = {
        "placement": 0.0,
        "industry_collaboration": 0.0,
        "accreditation": 0.0
    }
    
    for curriculum in curricula:
        if curriculum.recommendations:
            readiness = curriculum.recommendations.get("readiness_scores", {})
            total_readiness["placement"] += readiness.get("placements", 0.0)
            total_readiness["industry_collaboration"] += readiness.get("industry_collaboration", 0.0)
            total_readiness["accreditation"] += readiness.get("accreditation", 0.0)
    
    count = len(curricula)
    return {
        "placement_readiness": (total_readiness["placement"] / count * 100) if count > 0 else 0.0,
        "industry_collaboration": (total_readiness["industry_collaboration"] / count * 100) if count > 0 else 0.0,
        "accreditation": (total_readiness["accreditation"] / count * 100) if count > 0 else 0.0,
        "total_curricula": count
    }
