from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.core.moderation import moderate_content
from app.models.user import User
from app.services.user_service import UserService
import logging

logger = logging.getLogger(__name__)

class ModerationService:
    """Service for content moderation and policy enforcement"""
    
    @staticmethod
    async def moderate_user_content(content: str, user: Optional[User], db: Session) -> Dict[str, Any]:
        """Moderate user content and handle violations"""
        # Get moderation result
        moderation_result = await moderate_content(content)
        
        # Handle blocking violations
        if ModerationService._should_block(moderation_result):
            updated_user = UserService.handle_user_violation(db, user, "BLOCK")
            return {
                "should_block": True,
                "should_warn": False,
                "violation_type": "BLOCKED",
                "warning_message": "Content blocked due to policy violations. Repeated violations may result in account suspension.",
                "updated_user": updated_user,
                "moderation_result": moderation_result
            }
        
        # Handle warning violations
        if ModerationService._should_warn(moderation_result):
            updated_user = UserService.handle_user_violation(db, user, "WARNING")
            remaining_violations = 5 - (getattr(updated_user, 'violation_count') if updated_user else 0)
            if remaining_violations < 0:
                remaining_violations = 0
            
            return {
                "should_block": False,
                "should_warn": True,
                "violation_type": "WARNING",
                "warning_message": f"Your message contains potentially inappropriate content. You have {remaining_violations} warnings remaining before account suspension.",
                "updated_user": updated_user,
                "moderation_result": moderation_result
            }
        
        # Content is clean
        return {
            "should_block": False,
            "should_warn": False,
            "violation_type": "CLEAN",
            "warning_message": None,
            "updated_user": user,
            "moderation_result": moderation_result
        }
    
    @staticmethod
    def _should_block(moderation_result: Dict[str, Any]) -> bool:
        """Check if content should be blocked"""
        return moderation_result.get('violation_type') == 'BLOCK'
    
    @staticmethod
    def _should_warn(moderation_result: Dict[str, Any]) -> bool:
        """Check if content should generate warning"""
        return moderation_result.get('violation_type') == 'WARNING' 