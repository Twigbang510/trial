from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.crud.crud_user import user_crud
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

class UserService:
    """Service for user-related business logic"""
    
    @staticmethod
    def validate_user_access(current_user: Optional[User], required_user_id: Optional[int] = None) -> User:
        """Validate user authentication and authorization"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if not bool(current_user.is_active):
            raise HTTPException(status_code=403, detail="Account suspended")
        
        if required_user_id and int(getattr(current_user, 'id')) != int(required_user_id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return current_user
    
    @staticmethod
    def check_user_status(user: Optional[User]) -> None:
        """Check if user account is active"""
        if user and not bool(user.is_active):
            raise HTTPException(
                status_code=403, 
                detail="Your account has been suspended due to policy violations. Please contact support."
            )
    
    @staticmethod
    def handle_user_violation(db: Session, user: Optional[User], violation_type: str) -> Optional[User]:
        """Handle user policy violations and return updated user"""
        if not user:
            return None
            
        updated_user = user_crud.increment_violation(
            db=db, 
            user=user, 
            violation_type=violation_type
        )
        
        log_level = logging.WARNING if violation_type == "BLOCK" else logging.INFO
        logger.log(log_level, f"User {user.id} content {violation_type.lower()}. Violations: {updated_user.violation_count}")
        
        if not bool(updated_user.is_active):
            raise HTTPException(
                status_code=403,
                detail="Your account has been suspended due to repeated policy violations. Please contact support."
            )
        
        return updated_user 