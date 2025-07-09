from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, user, chatbot, career_analysis
from app.db.init_db import init_db
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Backend is running"}

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(user.router, prefix="/api/v1/users", tags=["users"])
app.include_router(chatbot.router, prefix="/api/v1/chatbot", tags=["chatbot"])
app.include_router(career_analysis.router, prefix="/api/v1/career-analysis", tags=["career-analysis"])

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db() 