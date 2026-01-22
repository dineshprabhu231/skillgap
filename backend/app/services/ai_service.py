"""
Google AI Studio (Gemini) integration service
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load .env file from backend directory
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Try new google.genai first, fallback to deprecated google.generativeai
USE_NEW_API = False
genai = None

try:
    from google import genai as new_genai
    USE_NEW_API = True
    print("✓ Using new google.genai package")
except ImportError:
    try:
        import google.generativeai as old_genai
        genai = old_genai
        print("⚠ Using deprecated google.generativeai package")
    except ImportError:
        raise ImportError("Please install google-genai: pip install google-genai")

class AIService:
    def __init__(self):
        # Try multiple locations for .env file
        backend_dir = Path(__file__).parent.parent.parent
        root_dir = backend_dir.parent if backend_dir.name == 'backend' else backend_dir
        
        env_paths = [
            backend_dir / '.env',  # backend/.env
            root_dir / '.env',     # root/.env
            Path.cwd() / '.env',   # current working directory
        ]
        
        env_loaded = False
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(dotenv_path=env_path, override=True)
                env_loaded = True
                print(f"✓ Loaded .env from: {env_path}")
                break
        
        # Also try default load_dotenv() which checks current directory
        if not env_loaded:
            load_dotenv(override=True)
        
        self.api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not self.api_key:
            checked_paths = "\n".join([f"  - {p} {'(EXISTS)' if p.exists() else '(NOT FOUND)'}" for p in env_paths])
            raise ValueError(
                f"GOOGLE_AI_API_KEY not found in environment variables.\n\n"
                f"Please create a .env file in the backend/ directory with:\n"
                f"GOOGLE_AI_API_KEY=your_api_key_here\n\n"
                f"Checked locations:\n{checked_paths}\n"
                f"Current working directory: {Path.cwd()}\n"
                f"Backend directory: {backend_dir}"
            )
        
        # Initialize based on which API is available
        if USE_NEW_API:
            # New google.genai API
            self.client = new_genai.Client(api_key=self.api_key)
            self.model_name = "gemini-2.0-flash"
            print(f"✓ Using Gemini model: {self.model_name} (new API)")
        else:
            # Old google.generativeai API
            genai.configure(api_key=self.api_key)
            model_names = ['gemini-1.5-flash-latest', 'gemini-1.5-pro-latest', 'gemini-pro']
            self.model = None
            
            for model_name in model_names:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    print(f"✓ Using Gemini model: {model_name} (old API)")
                    break
                except Exception as e:
                    print(f"  Model {model_name} not available: {e}")
                    continue
            
            if self.model is None:
                raise ValueError("No Gemini model available. Please check your API key and quota.")
        
        # Verify API key works (skip to avoid rate limits)
        # self._verify_api_key()
        print("✓ AI Service initialized (skipping verification to avoid rate limits)")
    
    def _generate_content(self, prompt: str, max_retries: int = 3) -> str:
        """Generate content using the appropriate API with retry logic"""
        import time
        
        for attempt in range(max_retries):
            try:
                if USE_NEW_API:
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=prompt
                    )
                    return response.text
                else:
                    response = self.model.generate_content(prompt)
                    return response.text if hasattr(response, 'text') else str(response)
            except Exception as e:
                error_str = str(e)
                if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 5  # 5s, 10s, 20s
                        print(f"  Rate limited, waiting {wait_time}s before retry {attempt + 2}/{max_retries}...")
                        time.sleep(wait_time)
                        continue
                raise e
        
        raise Exception("Max retries exceeded")
    
    def _verify_api_key(self):
        """Verify that the API key is valid by making a test call"""
        try:
            test_response = self._generate_content("Say 'API key is working' if you can read this.")
            print("✓ Google AI Studio API key verified successfully")
        except Exception as e:
            print(f"⚠ Warning: Could not verify API key: {e}")
            print("  The API key might be invalid or you may have hit rate limits.")
            print("  The service will still attempt to work, but may fail on actual requests.")
    
    def _extract_skills_fallback(self, text: str) -> List[str]:
        """Fallback skill extraction using keyword matching when AI is unavailable"""
        # Common skills to look for
        skill_keywords = [
            # Programming languages
            "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust", "Ruby", "PHP",
            # AI/ML
            "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Keras", "NLP", "Computer Vision",
            "Natural Language Processing", "LLM", "Neural Networks", "AI", "Data Science",
            # Web Development
            "React", "Angular", "Vue", "Node.js", "Express", "Django", "Flask", "FastAPI", "REST API",
            "HTML", "CSS", "Bootstrap", "Tailwind",
            # Data
            "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Pandas", "NumPy", "Data Analysis",
            "Data Visualization", "Tableau", "Power BI",
            # Cloud & DevOps
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "CI/CD", "DevOps", "Linux", "Git",
            # Soft Skills
            "Communication", "Leadership", "Problem Solving", "Team Collaboration", "Project Management",
        ]
        
        found_skills = []
        text_lower = text.lower()
        for skill in skill_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills[:20]  # Limit to 20 skills
    
    def extract_skills_from_resume(self, resume_text: str) -> List[str]:
        """Extract skills from resume text using AI"""
        prompt = f"""
        Analyze the following resume text and extract all technical and soft skills mentioned.
        Return only a JSON array of skill names, without any additional text.
        
        Resume text:
        {resume_text}
        
        Example output format: ["Python", "Machine Learning", "Communication", "Project Management"]
        """
        
        try:
            skills_text = self._generate_content(prompt).strip()
            # Remove markdown code blocks if present
            if skills_text.startswith("```"):
                skills_text = skills_text.split("```")[1]
                if skills_text.startswith("json"):
                    skills_text = skills_text[4:]
            skills_text = skills_text.strip()
            
            import json
            skills = json.loads(skills_text)
            return skills if isinstance(skills, list) else []
        except Exception as e:
            print(f"Error extracting skills from resume: {e}")
            print(f"  Using fallback keyword extraction...")
            return self._extract_skills_fallback(resume_text)
    
    def extract_skills_from_curriculum(self, curriculum_text: str) -> List[str]:
        """Extract skills from curriculum/syllabus text"""
        prompt = f"""
        Analyze the following academic curriculum/syllabus and extract all skills, technologies, 
        and competencies that students would learn from this curriculum.
        Return only a JSON array of skill names.
        
        Curriculum text:
        {curriculum_text}
        
        Example output format: ["Data Structures", "Algorithms", "Database Management", "Software Engineering"]
        """
        
        try:
            skills_text = self._generate_content(prompt).strip()
            if skills_text.startswith("```"):
                skills_text = skills_text.split("```")[1]
                if skills_text.startswith("json"):
                    skills_text = skills_text[4:]
            skills_text = skills_text.strip()
            
            import json
            skills = json.loads(skills_text)
            return skills if isinstance(skills, list) else []
        except Exception as e:
            print(f"Error extracting curriculum skills: {e}")
            print(f"  Using fallback keyword extraction...")
            return self._extract_skills_fallback(curriculum_text)
    
    def _generate_fallback_roadmap(
        self,
        current_skills: List[str],
        target_role: str,
        timeline_months: int,
        domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a basic fallback roadmap when AI is unavailable"""
        # Define common role skill requirements
        role_skills = {
            "data scientist": ["Python", "Statistics", "Machine Learning", "SQL", "Data Visualization", "Deep Learning"],
            "machine learning engineer": ["Python", "TensorFlow", "PyTorch", "MLOps", "Cloud Computing", "Docker"],
            "software engineer": ["Python", "JavaScript", "Git", "APIs", "Databases", "System Design"],
            "web developer": ["HTML", "CSS", "JavaScript", "React", "Node.js", "Databases"],
            "devops engineer": ["Linux", "Docker", "Kubernetes", "CI/CD", "Cloud Platforms", "Scripting"],
            "cybersecurity analyst": ["Network Security", "Linux", "Python", "Penetration Testing", "SIEM", "Compliance"],
            "ai engineer": ["Python", "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "MLOps"],
        }
        
        # Find matching role or use default
        target_lower = target_role.lower()
        required_skills = []
        for role, skills in role_skills.items():
            if role in target_lower or target_lower in role:
                required_skills = skills
                break
        
        if not required_skills:
            required_skills = ["Programming", "Problem Solving", "Communication", "Project Management", "Domain Knowledge", "Continuous Learning"]
        
        # Filter out skills user already has
        current_lower = [s.lower() for s in current_skills]
        skills_to_learn = [s for s in required_skills if s.lower() not in current_lower]
        
        if not skills_to_learn:
            skills_to_learn = ["Advanced " + required_skills[0] if required_skills else "Advanced Skills"]
        
        # Calculate time per skill
        weeks_per_skill = max(2, (timeline_months * 4) // len(skills_to_learn))
        
        steps = []
        for i, skill in enumerate(skills_to_learn[:6], 1):  # Limit to 6 steps
            steps.append({
                "step_number": i,
                "skill": skill,
                "prerequisites": [skills_to_learn[i-2]] if i > 1 else current_skills[:2] if current_skills else [],
                "estimated_time_weeks": weeks_per_skill,
                "suggested_courses": [f"Introduction to {skill}", f"Advanced {skill}"],
                "suggested_certifications": [f"{skill} Certification"] if i <= 3 else [],
                "mini_projects": [f"Build a {skill.lower()} project", f"Practice {skill.lower()} exercises"],
                "description": f"Learn {skill} fundamentals and apply them to real-world problems"
            })
        
        return {
            "title": f"Roadmap to become {target_role}",
            "steps": steps,
            "total_estimated_weeks": len(steps) * weeks_per_skill,
            "capstone_ideas": [
                f"Build a complete {target_role.lower()} portfolio project",
                f"Contribute to open-source {domain or target_role.lower()} projects"
            ],
            "note": "This is a basic roadmap generated offline. For personalized recommendations, please try again later."
        }

    def generate_skill_roadmap(
        self, 
        current_skills: List[str],
        target_role: str,
        timeline_months: int,
        domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate personalized learning roadmap using AI"""
        skills_str = ", ".join(current_skills) if current_skills else "None"
        domain_str = f" in the {domain} domain" if domain else ""
        
        prompt = f"""
        Create a detailed, step-by-step learning roadmap for someone who wants to become a {target_role}{domain_str}.
        
        Current skills: {skills_str}
        Target timeline: {timeline_months} months
        
        Generate a comprehensive roadmap with:
        1. Step-by-step learning path
        2. Prerequisites for each step
        3. Estimated time for each step (in weeks)
        4. Suggested online courses
        5. Recommended certifications
        6. Mini-projects to practice
        7. Capstone project ideas
        
        Return the response as a JSON object with this structure:
        {{
            "title": "Roadmap to become {target_role}",
            "steps": [
                {{
                    "step_number": 1,
                    "skill": "Skill name",
                    "prerequisites": ["prereq1", "prereq2"],
                    "estimated_time_weeks": 4,
                    "suggested_courses": ["course1", "course2"],
                    "suggested_certifications": ["cert1"],
                    "mini_projects": ["project1", "project2"],
                    "description": "What to learn in this step"
                }}
            ],
            "total_estimated_weeks": 52,
            "capstone_ideas": ["idea1", "idea2"]
        }}
        """
        
        try:
            roadmap_text = self._generate_content(prompt).strip()
            if roadmap_text.startswith("```"):
                roadmap_text = roadmap_text.split("```")[1]
                if roadmap_text.startswith("json"):
                    roadmap_text = roadmap_text[4:]
            roadmap_text = roadmap_text.strip()
            
            import json
            roadmap = json.loads(roadmap_text)
            return roadmap
        except Exception as e:
            print(f"Error generating roadmap with AI: {e}")
            print(f"  Using fallback roadmap generation...")
            return self._generate_fallback_roadmap(current_skills, target_role, timeline_months, domain)
    
    def _analyze_gaps_fallback(
        self,
        current_skills: List[str],
        required_skills: List[str],
        target_role: str
    ) -> Dict[str, Any]:
        """Fallback gap analysis when AI is unavailable"""
        current_lower = set(s.lower() for s in current_skills)
        required_lower = set(s.lower() for s in required_skills)
        
        # Find missing skills
        missing = [s for s in required_skills if s.lower() not in current_lower]
        
        # Calculate gap score (percentage of missing skills)
        if required_skills:
            gap_score = 1 - (len(missing) / len(required_skills))
        else:
            gap_score = 1.0
        
        # Split missing into short-term and long-term priorities
        half = len(missing) // 2
        short_term = missing[:half] if half > 0 else missing[:3]
        long_term = missing[half:] if half > 0 else missing[3:]
        
        return {
            "missing_skills": missing,
            "priority_skills_short_term": short_term[:5],
            "priority_skills_long_term": long_term[:5],
            "gap_score": round(gap_score, 2),
            "recommendations": f"To become a {target_role}, focus first on learning: {', '.join(short_term[:3]) if short_term else 'advanced skills in your current areas'}. You have {len(current_skills)} skills and need to learn {len(missing)} more.",
            "note": "This is a basic analysis generated offline. For detailed AI recommendations, please try again later."
        }

    def analyze_skill_gaps(
        self,
        current_skills: List[str],
        required_skills: List[str],
        target_role: str
    ) -> Dict[str, Any]:
        """Analyze skill gaps and provide recommendations"""
        current_str = ", ".join(current_skills) if current_skills else "None"
        required_str = ", ".join(required_skills)
        
        prompt = f"""
        Analyze the skill gap between current skills and required skills for the role: {target_role}
        
        Current skills: {current_str}
        Required skills: {required_str}
        
        Provide analysis in JSON format:
        {{
            "missing_skills": ["skill1", "skill2"],
            "priority_skills_short_term": ["skill1", "skill2"],
            "priority_skills_long_term": ["skill3", "skill4"],
            "gap_score": 0.65,
            "recommendations": "Detailed text recommendations"
        }}
        """
        
        try:
            analysis_text = self._generate_content(prompt).strip()
            if analysis_text.startswith("```"):
                analysis_text = analysis_text.split("```")[1]
                if analysis_text.startswith("json"):
                    analysis_text = analysis_text[4:]
            analysis_text = analysis_text.strip()
            
            import json
            analysis = json.loads(analysis_text)
            return analysis
        except Exception as e:
            print(f"Error analyzing skill gaps with AI: {e}")
            print(f"  Using fallback gap analysis...")
            return self._analyze_gaps_fallback(current_skills, required_skills, target_role)
    
    def _curriculum_recommendations_fallback(
        self,
        current_curriculum_skills: List[str],
        industry_skills: List[str],
        future_skills: List[str]
    ) -> Dict[str, Any]:
        """Fallback curriculum recommendations when AI is unavailable"""
        current_lower = set(s.lower() for s in current_curriculum_skills)
        industry_lower = set(s.lower() for s in industry_skills)
        future_lower = set(s.lower() for s in future_skills)
        
        # Skills to add (in industry or future but not in curriculum)
        skills_to_add = [s for s in industry_skills if s.lower() not in current_lower]
        skills_to_add += [s for s in future_skills if s.lower() not in current_lower and s.lower() not in set(sk.lower() for sk in skills_to_add)]
        
        # Skills that might be outdated (in curriculum but not in industry or future)
        combined_required = industry_lower | future_lower
        skills_to_reduce = [s for s in current_curriculum_skills if s.lower() not in combined_required]
        
        # Calculate alignment score
        if industry_skills:
            industry_match = len([s for s in current_curriculum_skills if s.lower() in industry_lower])
            alignment = industry_match / len(industry_skills)
        else:
            alignment = 0.5
        
        return {
            "skills_to_add": skills_to_add[:10],
            "skills_to_remove": [],
            "skills_to_reduce_focus": skills_to_reduce[:5],
            "lab_suggestions": [f"{s} practical lab" for s in skills_to_add[:3]],
            "project_suggestions": [f"Build a project using {s}" for s in skills_to_add[:3]],
            "alignment_score": round(alignment, 2),
            "readiness_scores": {
                "placements": round(alignment * 0.9, 2),
                "industry_collaboration": round(alignment * 0.85, 2),
                "accreditation": round(min(alignment + 0.1, 1.0), 2)
            },
            "detailed_recommendations": f"Consider adding {len(skills_to_add)} new skills to align with industry demands. Focus on: {', '.join(skills_to_add[:5]) if skills_to_add else 'maintaining current curriculum'}.",
            "note": "This is a basic analysis generated offline. For detailed AI recommendations, please try again later."
        }

    def generate_curriculum_recommendations(
        self,
        current_curriculum_skills: List[str],
        industry_skills: List[str],
        future_skills: List[str]
    ) -> Dict[str, Any]:
        """Generate curriculum improvement recommendations"""
        current_str = ", ".join(current_curriculum_skills)
        industry_str = ", ".join(industry_skills)
        future_str = ", ".join(future_skills)
        
        prompt = f"""
        Analyze an academic curriculum and provide recommendations for improvement.
        
        Current curriculum skills: {current_str}
        Industry-required skills: {industry_str}
        Future-emerging skills: {future_str}
        
        Provide recommendations in JSON format:
        {{
            "skills_to_add": ["skill1", "skill2"],
            "skills_to_remove": ["skill3"],
            "skills_to_reduce_focus": ["skill4"],
            "lab_suggestions": ["lab1", "lab2"],
            "project_suggestions": ["project1", "project2"],
            "alignment_score": 0.7,
            "readiness_scores": {{
                "placements": 0.65,
                "industry_collaboration": 0.70,
                "accreditation": 0.75
            }},
            "detailed_recommendations": "Text explanation"
        }}
        """
        
        try:
            rec_text = self._generate_content(prompt).strip()
            if rec_text.startswith("```"):
                rec_text = rec_text.split("```")[1]
                if rec_text.startswith("json"):
                    rec_text = rec_text[4:]
            rec_text = rec_text.strip()
            
            import json
            recommendations = json.loads(rec_text)
            return recommendations
        except Exception as e:
            print(f"Error generating curriculum recommendations with AI: {e}")
            print(f"  Using fallback curriculum recommendations...")
            return self._curriculum_recommendations_fallback(
                current_curriculum_skills, industry_skills, future_skills
            )
