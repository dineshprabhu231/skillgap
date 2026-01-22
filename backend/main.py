"""
Skill Gap Intelligence Platform - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.database import engine, Base, SessionLocal
from app.models import User, Skill
from app.routers import skills, roadmaps, curriculum, analytics
from app.services.ai_service import AIService
from app.services.trends_service import TrendsService

# Load .env file explicitly from backend directory
from pathlib import Path
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Initialize services (lazy-loaded in routers, not here)
trends_service = TrendsService()

def init_default_data():
    """Initialize default user and skills if they don't exist"""
    db = SessionLocal()
    try:
        # Create default user if not exists
        default_user = db.query(User).filter(User.id == 1).first()
        if not default_user:
            print("  Creating default user...")
            default_user = User(
                id=1,
                email="demo@sgip.com",
                hashed_password="demo_password_hash",
                full_name="Demo User",
                user_type="student",
                is_active=True
            )
            db.add(default_user)
            db.commit()
            print("  ✓ Default user created")
        
        # Check if skills exist
        skill_count = db.query(Skill).count()
        if skill_count == 0:
            print("  Seeding initial skills...")
            initial_skills = [
                {"name": "Python", "category": "Technical", "domain": "AI", "current_demand_score": 85.0, "future_demand_score": 90.0, "trend_status": "high-growth"},
                {"name": "Machine Learning", "category": "Technical", "domain": "AI", "current_demand_score": 80.0, "future_demand_score": 92.0, "trend_status": "high-growth"},
                {"name": "Deep Learning", "category": "Technical", "domain": "AI", "current_demand_score": 75.0, "future_demand_score": 88.0, "trend_status": "high-growth"},
                {"name": "Natural Language Processing", "category": "Technical", "domain": "AI", "current_demand_score": 70.0, "future_demand_score": 85.0, "trend_status": "emerging"},
                {"name": "TensorFlow", "category": "Technical", "domain": "AI", "current_demand_score": 70.0, "future_demand_score": 75.0, "trend_status": "saturated"},
                {"name": "PyTorch", "category": "Technical", "domain": "AI", "current_demand_score": 75.0, "future_demand_score": 85.0, "trend_status": "high-growth"},
                {"name": "LLM Fine-tuning", "category": "Technical", "domain": "AI", "current_demand_score": 60.0, "future_demand_score": 95.0, "trend_status": "emerging"},
                {"name": "JavaScript", "category": "Technical", "domain": "Software Engineering", "current_demand_score": 85.0, "future_demand_score": 80.0, "trend_status": "saturated"},
                {"name": "TypeScript", "category": "Technical", "domain": "Software Engineering", "current_demand_score": 80.0, "future_demand_score": 90.0, "trend_status": "high-growth"},
                {"name": "React", "category": "Technical", "domain": "Software Engineering", "current_demand_score": 85.0, "future_demand_score": 85.0, "trend_status": "saturated"},
                {"name": "Node.js", "category": "Technical", "domain": "Software Engineering", "current_demand_score": 80.0, "future_demand_score": 80.0, "trend_status": "saturated"},
                {"name": "Docker", "category": "Technical", "domain": "Software Engineering", "current_demand_score": 75.0, "future_demand_score": 85.0, "trend_status": "high-growth"},
                {"name": "Kubernetes", "category": "Technical", "domain": "Software Engineering", "current_demand_score": 70.0, "future_demand_score": 88.0, "trend_status": "high-growth"},
                {"name": "AWS", "category": "Technical", "domain": "Software Engineering", "current_demand_score": 85.0, "future_demand_score": 90.0, "trend_status": "high-growth"},
                {"name": "Data Analysis", "category": "Technical", "domain": "Data Science", "current_demand_score": 80.0, "future_demand_score": 85.0, "trend_status": "high-growth"},
                {"name": "SQL", "category": "Technical", "domain": "Data Science", "current_demand_score": 85.0, "future_demand_score": 80.0, "trend_status": "saturated"},
                {"name": "Pandas", "category": "Technical", "domain": "Data Science", "current_demand_score": 75.0, "future_demand_score": 80.0, "trend_status": "saturated"},
                {"name": "Blockchain", "category": "Technical", "domain": "FinTech", "current_demand_score": 55.0, "future_demand_score": 70.0, "trend_status": "high-growth"},
                {"name": "Penetration Testing", "category": "Technical", "domain": "Cybersecurity", "current_demand_score": 75.0, "future_demand_score": 85.0, "trend_status": "high-growth"},
                {"name": "Healthcare Data Analysis", "category": "Domain-specific", "domain": "Healthcare", "current_demand_score": 65.0, "future_demand_score": 80.0, "trend_status": "high-growth"},
            ]
            for skill_data in initial_skills:
                db.add(Skill(**skill_data))
            db.commit()
            print(f"  ✓ Added {len(initial_skills)} initial skills")
        else:
            print(f"  ✓ Skills already exist ({skill_count} skills)")
    except Exception as e:
        print(f"  ⚠ Warning: Could not initialize default data: {e}")
        db.rollback()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        # Try to create database tables
        Base.metadata.create_all(bind=engine)
        print("✓ Database connection successful")
        # Initialize default data
        init_default_data()
    except Exception as e:
        print(f"⚠ Warning: Could not connect to database: {e}")
        print("  The server will start, but database features may not work.")
        print("  Make sure PostgreSQL is running and DATABASE_URL is correct in .env")
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Skill Gap Intelligence Platform API",
    description="AI-powered skill intelligence and forecasting platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (authentication removed for now)
app.include_router(skills.router, prefix="/api/skills", tags=["Skills"])
app.include_router(roadmaps.router, prefix="/api/roadmaps", tags=["Roadmaps"])
app.include_router(curriculum.router, prefix="/api/curriculum", tags=["Curriculum"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

@app.get("/")
async def root():
    return {
        "message": "Skill Gap Intelligence Platform API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
