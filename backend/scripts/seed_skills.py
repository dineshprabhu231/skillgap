"""
Seed script to populate initial skills data
Run this after setting up the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import Skill
from app.services.trends_service import TrendsService

def seed_skills():
    """Seed initial skills into the database"""
    db = SessionLocal()
    trends_service = TrendsService()
    
    # Initial skills to seed
    initial_skills = [
        # AI/ML Skills
        {"name": "Python", "category": "Technical", "domain": "AI", "description": "Programming language"},
        {"name": "Machine Learning", "category": "Technical", "domain": "AI", "description": "ML algorithms and models"},
        {"name": "Deep Learning", "category": "Technical", "domain": "AI", "description": "Neural networks and deep learning"},
        {"name": "Natural Language Processing", "category": "Technical", "domain": "AI", "description": "NLP techniques"},
        {"name": "Computer Vision", "category": "Technical", "domain": "AI", "description": "Image and video processing"},
        {"name": "TensorFlow", "category": "Technical", "domain": "AI", "description": "ML framework"},
        {"name": "PyTorch", "category": "Technical", "domain": "AI", "description": "ML framework"},
        
        # Healthcare Skills
        {"name": "Healthcare Data Analysis", "category": "Domain-specific", "domain": "Healthcare", "description": "Medical data analysis"},
        {"name": "HIPAA Compliance", "category": "Domain-specific", "domain": "Healthcare", "description": "Healthcare regulations"},
        {"name": "Electronic Health Records", "category": "Domain-specific", "domain": "Healthcare", "description": "EHR systems"},
        
        # FinTech Skills
        {"name": "Blockchain", "category": "Technical", "domain": "FinTech", "description": "Blockchain technology"},
        {"name": "Cryptocurrency", "category": "Domain-specific", "domain": "FinTech", "description": "Digital currencies"},
        {"name": "Financial Modeling", "category": "Domain-specific", "domain": "FinTech", "description": "Financial analysis"},
        
        # Cybersecurity Skills
        {"name": "Penetration Testing", "category": "Technical", "domain": "Cybersecurity", "description": "Security testing"},
        {"name": "Network Security", "category": "Technical", "domain": "Cybersecurity", "description": "Network protection"},
        {"name": "Security Auditing", "category": "Technical", "domain": "Cybersecurity", "description": "Security assessment"},
        
        # General Software Engineering
        {"name": "JavaScript", "category": "Technical", "domain": "Software Engineering", "description": "Web programming"},
        {"name": "React", "category": "Technical", "domain": "Software Engineering", "description": "Frontend framework"},
        {"name": "Node.js", "category": "Technical", "domain": "Software Engineering", "description": "Backend runtime"},
        {"name": "Docker", "category": "Technical", "domain": "Software Engineering", "description": "Containerization"},
        {"name": "Kubernetes", "category": "Technical", "domain": "Software Engineering", "description": "Container orchestration"},
        {"name": "AWS", "category": "Technical", "domain": "Software Engineering", "description": "Cloud platform"},
        {"name": "DevOps", "category": "Technical", "domain": "Software Engineering", "description": "Development operations"},
        
        # Data Science
        {"name": "Data Analysis", "category": "Technical", "domain": "Data Science", "description": "Data exploration"},
        {"name": "SQL", "category": "Technical", "domain": "Data Science", "description": "Database queries"},
        {"name": "Pandas", "category": "Technical", "domain": "Data Science", "description": "Data manipulation"},
        {"name": "Data Visualization", "category": "Technical", "domain": "Data Science", "description": "Creating charts and graphs"},
    ]
    
    print("Seeding skills...")
    skills_added = 0
    
    for skill_data in initial_skills:
        # Check if skill already exists
        existing = db.query(Skill).filter(Skill.name == skill_data["name"]).first()
        if not existing:
            skill = Skill(**skill_data)
            db.add(skill)
            skills_added += 1
    
    db.commit()
    print(f"Added {skills_added} new skills")
    
    # Update trend data for existing skills
    print("Updating trend data...")
    all_skills = db.query(Skill).all()
    skill_names = [s.name for s in all_skills]
    
    # Get trends for all skills (in batches to avoid rate limits)
    batch_size = 5
    for i in range(0, len(skill_names), batch_size):
        batch = skill_names[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}...")
        
        try:
            trend_analyses = trends_service.analyze_multiple_skills(batch)
            
            for analysis in trend_analyses:
                skill = db.query(Skill).filter(Skill.name == analysis["skill"]).first()
                if skill:
                    skill.current_demand_score = analysis["current_demand"]
                    skill.future_demand_score = analysis["forecasts"]["forecast_1y"]
                    skill.trend_status = analysis["trend_status"]
                    skill.google_trends_score = analysis["current_demand"]
                    skill.forecast_6m = analysis["forecasts"]["forecast_6m"]
                    skill.forecast_1y = analysis["forecasts"]["forecast_1y"]
                    skill.forecast_3y = analysis["forecasts"]["forecast_3y"]
            
            db.commit()
        except Exception as e:
            print(f"Error processing batch: {e}")
            continue
    
    print("Trend data updated!")
    db.close()

if __name__ == "__main__":
    seed_skills()
