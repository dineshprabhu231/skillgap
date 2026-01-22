# Skill Gap Intelligence Platform (SGIP)

An AI-powered skill intelligence platform that analyzes job markets, academic curricula, and global search trends to predict emerging skills and guide learners and institutions toward future-ready education and careers.

## Features

- **Skill Gap Analysis**: AI-powered extraction and comparison of current vs. required skills
- **Market Demand Forecasting**: Real-time skill demand prediction using Google Trends and job market data
- **Personalized Roadmaps**: AI-generated learning paths tailored to individual goals
- **Curriculum Alignment**: Institutional curriculum analysis and improvement recommendations
- **Visual Dashboards**: Interactive analytics and trend visualizations

## Tech Stack

- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.11+
- **AI/ML**: Google AI Studio (Gemini API)
- **Database**: PostgreSQL
- **Data Sources**: Google Trends API, Job market APIs

## Project Structure

```
.
├── backend/          # FastAPI backend
├── frontend/         # Next.js frontend
├── docs/            # Documentation
└── README.md
```

## Setup Instructions

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

Create `.env` files in both `backend/` and `frontend/` directories with:

**Backend (.env)**
```
GOOGLE_AI_API_KEY=your_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/sgip_db
SECRET_KEY=your_secret_key_here
```

**Frontend (.env.local)**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

## License

MIT
