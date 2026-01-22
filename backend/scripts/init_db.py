"""
Initialize database with required data for the application to work
Run this after starting the backend server for the first time
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models import User, Skill

def init_database():
    """Initialize the database with required data"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Create default user if not exists
        default_user = db.query(User).filter(User.id == 1).first()
        if not default_user:
            print("Creating default user...")
            default_user = User(
                id=1,
                email="demo@sgip.com",
                hashed_password="demo_password_hash",  # Not used since auth is disabled
                full_name="Demo User",
                user_type="student",
                is_active=True
            )
            db.add(default_user)
            db.commit()
            print("✓ Default user created (ID: 1)")
        else:
            print("✓ Default user already exists")
        
        # Seed initial skills
        initial_skills = [
            # AI/ML Skills
            {"name": "Python", "category": "Technical", "domain": "AI", "description": "Programming language for AI/ML", "current_demand_score": 85.0, "future_demand_score": 90.0, "trend_status": "high-growth"},
            {"name": "Machine Learning", "category": "Technical", "domain": "AI", "description": "ML algorithms and models", "current_demand_score": 80.0, "future_demand_score": 92.0, "trend_status": "high-growth"},
            {"name": "Deep Learning", "category": "Technical", "domain": "AI", "description": "Neural networks and deep learning", "current_demand_score": 75.0, "future_demand_score": 88.0, "trend_status": "high-growth"},
            {"name": "Natural Language Processing", "category": "Technical", "domain": "AI", "description": "NLP techniques", "current_demand_score": 70.0, "future_demand_score": 85.0, "trend_status": "emerging"},
            {"name": "Computer Vision", "category": "Technical", "domain": "AI", "description": "Image and video processing", "current_demand_score": 65.0, "future_demand_score": 80.0, "trend_status": "emerging"},
            {"name": "TensorFlow", "category": "Technical", "domain": "AI", "description": "ML framework by Google", "current_demand_score": 70.0, "future_demand_score": 75.0, "trend_status": "saturated"},
            {"name": "PyTorch", "category": "Technical", "domain": "AI", "description": "ML framework by Meta", "current_demand_score": 75.0, "future_demand_score": 85.0, "trend_status": "high-growth"},
            {"name": "LLM Fine-tuning", "category": "Technical", "domain": "AI", "description": "Large Language Model customization", "current_demand_score": 60.0, "future_demand_score": 95.0, "trend_status": "emerging"},
            {"name": "Prompt Engineering", "category": "Technical", "domain": "AI", "description": "Designing effective AI prompts", "current_demand_score": 55.0, "future_demand_score": 90.0, "trend_status": "emerging"},
            
            # Healthcare Skills
            {"name": "Healthcare Data Analysis", "category": "Domain-specific", "domain": "Healthcare", "description": "Medical data analysis", "current_demand_score": 65.0, "future_demand_score": 80.0, "trend_status": "high-growth"},
            {"name": "HIPAA Compliance", "category": "Domain-specific", "domain": "Healthcare", "description": "Healthcare regulations", "current_demand_score": 60.0, "future_demand_score": 65.0, "trend_status": "saturated"},
            {"name": "Electronic Health Records", "category": "Domain-specific", "domain": "Healthcare", "description": "EHR systems", "current_demand_score": 55.0, "future_demand_score": 60.0, "trend_status": "saturated"},
            {"name": "Medical Imaging AI", "category": "Technical", "domain": "Healthcare", "description": "AI for medical imaging", "current_demand_score": 50.0, "future_demand_score": 85.0, "trend_status": "emerging"},
            
            # FinTech Skills
            {"name": "Blockchain", "category": "Technical", "domain": "FinTech", "description": "Blockchain technology", "current_demand_score": 55.0, "future_demand_score": 70.0, "trend_status": "high-growth"},
            {"name": "Cryptocurrency", "category": "Domain-specific", "domain": "FinTech", "description": "Digital currencies", "current_demand_score": 45.0, "future_demand_score": 60.0, "trend_status": "saturated"},
            {"name": "Financial Modeling", "category": "Domain-specific", "domain": "FinTech", "description": "Financial analysis", "current_demand_score": 70.0, "future_demand_score": 75.0, "trend_status": "saturated"},
            {"name": "Algorithmic Trading", "category": "Technical", "domain": "FinTech", "description": "Automated trading systems", "current_demand_score": 60.0, "future_demand_score": 75.0, "trend_status": "high-growth"},
            
            # Cybersecurity Skills
            {"name": "Penetration Testing", "category": "Technical", "domain": "Cybersecurity", "description": "Security testing", "current_demand_score": 75.0, "future_demand_score": 85.0, "trend_status": "high-growth"},
            {"name": "Network Security", "category": "Technical", "domain": "Cybersecurity", "description": "Network protection", "current_demand_score": 70.0, "future_demand_score": 75.0, "trend_status": "saturated"},
            {"name": "Security Auditing", "category": "Technical", "domain": "Cybersecurity", "description": "Security assessment", "current_demand_score": 65.0, "future_demand_score": 70.0, "trend_status": "saturated"},
            {"name": "Cloud Security", "category": "Technical", "domain": "Cybersecurity", "description": "Securing cloud infrastructure", "current_demand_score": 70.0, "future_demand_score": 90.0, "trend_status": "emerging"},
            
            # Software Engineering
            {"name": "JavaScript", "category": "Technical", "domain": "Software Engineering", "description": "Web programming", "current_demand_score": 85.0, "future_demand_score": 80.0, "trend_status": "saturated"},
            {"name": "TypeScript", "category": "Technical", "domain": "Software Engineering", "description": "Typed JavaScript", "current_demand_score": 80.0, "future_demand_score": 90.0, "trend_status": "high-growth"},
            {"name": "React", "category": "Technical", "domain": "Software Engineering", "description": "Frontend framework", "current_demand_score": 85.0, "future_demand_score": 85.0, "trend_status": "saturated"},
            {"name": "Node.js", "category": "Technical", "domain": "Software Engineering", "description": "Backend runtime", "current_demand_score": 80.0, "future_demand_score": 80.0, "trend_status": "saturated"},
            {"name": "Docker", "category": "Technical", "domain": "Software Engineering", "description": "Containerization", "current_demand_score": 75.0, "future_demand_score": 85.0, "trend_status": "high-growth"},
            {"name": "Kubernetes", "category": "Technical", "domain": "Software Engineering", "description": "Container orchestration", "current_demand_score": 70.0, "future_demand_score": 88.0, "trend_status": "high-growth"},
            {"name": "AWS", "category": "Technical", "domain": "Software Engineering", "description": "Cloud platform", "current_demand_score": 85.0, "future_demand_score": 90.0, "trend_status": "high-growth"},
            {"name": "DevOps", "category": "Technical", "domain": "Software Engineering", "description": "Development operations", "current_demand_score": 80.0, "future_demand_score": 88.0, "trend_status": "high-growth"},
            {"name": "CI/CD", "category": "Technical", "domain": "Software Engineering", "description": "Continuous Integration/Deployment", "current_demand_score": 75.0, "future_demand_score": 85.0, "trend_status": "high-growth"},
            {"name": "Microservices", "category": "Technical", "domain": "Software Engineering", "description": "Microservices architecture", "current_demand_score": 70.0, "future_demand_score": 80.0, "trend_status": "high-growth"},
            
            # Data Science
            {"name": "Data Analysis", "category": "Technical", "domain": "Data Science", "description": "Data exploration", "current_demand_score": 80.0, "future_demand_score": 85.0, "trend_status": "high-growth"},
            {"name": "SQL", "category": "Technical", "domain": "Data Science", "description": "Database queries", "current_demand_score": 85.0, "future_demand_score": 80.0, "trend_status": "saturated"},
            {"name": "Pandas", "category": "Technical", "domain": "Data Science", "description": "Data manipulation", "current_demand_score": 75.0, "future_demand_score": 80.0, "trend_status": "saturated"},
            {"name": "Data Visualization", "category": "Technical", "domain": "Data Science", "description": "Creating charts and graphs", "current_demand_score": 70.0, "future_demand_score": 75.0, "trend_status": "saturated"},
            {"name": "Statistical Analysis", "category": "Technical", "domain": "Data Science", "description": "Statistical methods", "current_demand_score": 70.0, "future_demand_score": 75.0, "trend_status": "saturated"},
            {"name": "Big Data", "category": "Technical", "domain": "Data Science", "description": "Large-scale data processing", "current_demand_score": 65.0, "future_demand_score": 80.0, "trend_status": "high-growth"},
            {"name": "Apache Spark", "category": "Technical", "domain": "Data Science", "description": "Big data processing framework", "current_demand_score": 60.0, "future_demand_score": 75.0, "trend_status": "high-growth"},
            
            # Soft Skills
            {"name": "Communication", "category": "Soft", "domain": "General", "description": "Effective communication", "current_demand_score": 90.0, "future_demand_score": 90.0, "trend_status": "saturated"},
            {"name": "Problem Solving", "category": "Soft", "domain": "General", "description": "Analytical thinking", "current_demand_score": 90.0, "future_demand_score": 92.0, "trend_status": "high-growth"},
            {"name": "Team Collaboration", "category": "Soft", "domain": "General", "description": "Working in teams", "current_demand_score": 85.0, "future_demand_score": 88.0, "trend_status": "saturated"},
            {"name": "Project Management", "category": "Soft", "domain": "General", "description": "Managing projects", "current_demand_score": 75.0, "future_demand_score": 80.0, "trend_status": "saturated"},
        ]
        
        skills_added = 0
        for skill_data in initial_skills:
            existing = db.query(Skill).filter(Skill.name == skill_data["name"]).first()
            if not existing:
                skill = Skill(**skill_data)
                db.add(skill)
                skills_added += 1
        
        db.commit()
        print(f"✓ Added {skills_added} new skills (Total: {db.query(Skill).count()} skills)")
        
        print("\n✓ Database initialization complete!")
        print("\nYou can now use the application:")
        print("  - Upload resumes at /dashboard/resume")
        print("  - Analyze skill gaps at /dashboard/gaps")
        print("  - Generate roadmaps at /dashboard/roadmap")
        print("  - View analytics at /dashboard/analytics")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
