from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.models.user import User
from app.schemas.career_analysis import (
    CareerAnalysisCreate, 
    CareerAnalysisResponse, 
    CareerChatContext
)
from app.services.career_analysis_service import career_analysis_service
from app.api.deps import get_db

router = APIRouter()


@router.post("/analyze", response_model=CareerAnalysisResponse)
async def create_career_analysis(
    *,
    db: Session = Depends(get_db),
    analysis_in: CareerAnalysisCreate,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Create new career analysis for current user using Gemini AI
    """
    try:
        # Create initial record in database
        career_analysis_record = crud.career_analysis.create_with_user(
            db=db, obj_in=analysis_in, user_id=current_user.id
        )
        
        # Generate AI analysis using Gemini
        ai_results = career_analysis_service.analyze_career_path(
            mbti_type=analysis_in.mbti_type,
            holland_scores=analysis_in.holland_scores
        )
        
        # Update record with AI results
        updated_record = crud.career_analysis.update_analysis_results(
            db=db,
            db_obj=career_analysis_record,
            personality_summary=ai_results.get("personality_summary", ""),
            holland_code=ai_results.get("holland_code", ""),
            career_suggestions=ai_results.get("career_suggestions", []),
            personality_traits=ai_results.get("personality_traits", []),
            strengths=ai_results.get("strengths", []),
            growth_areas=ai_results.get("growth_areas", []),
            detailed_analysis=ai_results.get("detailed_analysis", ""),
            recommendations=ai_results.get("recommendations", "")
        )
        
        return updated_record
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze career path: {str(e)}"
        )


@router.get("/my-analyses", response_model=List[CareerAnalysisResponse])
def get_my_career_analyses(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 10
):
    """
    Get all career analyses for current user
    """
    analyses = crud.career_analysis.get_by_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return analyses


@router.get("/latest", response_model=CareerAnalysisResponse)
def get_latest_career_analysis(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get the most recent career analysis for current user
    """
    analysis = crud.career_analysis.get_latest_by_user(
        db=db, user_id=current_user.id
    )
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No career analysis found for this user"
        )
    
    return analysis


@router.get("/{analysis_id}", response_model=CareerAnalysisResponse)
def get_career_analysis(
    *,
    db: Session = Depends(get_db),
    analysis_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get a specific career analysis by ID
    """
    analysis = crud.career_analysis.get(db=db, id=analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career analysis not found"
        )
    
    # Check if analysis belongs to current user
    if analysis.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return analysis


@router.post("/chat")
async def career_chat(
    *,
    db: Session = Depends(get_db),
    chat_context: CareerChatContext,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Generate AI response for career-related questions based on user's analysis
    """
    # Get the career analysis
    analysis = crud.career_analysis.get(db=db, id=chat_context.analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career analysis not found"
        )
    
    # Check if analysis belongs to current user
    if analysis.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Prepare career context for AI
    career_context = {
        "mbti_type": analysis.mbti_type,
        "holland_code": analysis.holland_code,
        "career_suggestions": analysis.career_suggestions or [],
        "personality_traits": analysis.personality_traits or [],
        "strengths": analysis.strengths or [],
        "growth_areas": analysis.growth_areas or []
    }
    
    try:
        # Generate AI response
        ai_response = career_analysis_service.generate_career_chat_response(
            analysis_id=chat_context.analysis_id,
            user_question=chat_context.user_question,
            career_context=career_context
        )
        
        return {
            "response": ai_response,
            "analysis_id": chat_context.analysis_id,
            "context": "career_guidance"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate career chat response: {str(e)}"
        ) 