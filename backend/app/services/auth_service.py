import logging
from typing import Optional, Dict, Any
from pymongo.database import Database
from fastapi import HTTPException
from datetime import timedelta
from app.crud.crud_user import user_crud
from app.schemas.user import UserCreate, UserOut, UserLogin
from app.core.security import create_access_token
from app.core.email import send_verification_email, send_password_reset_email
from app.core.config import settings

logger = logging.getLogger(__name__)

# In-memory storage for verification codes (in production, use Redis or database)
verification_codes = {}
reset_codes = {}

class AuthService:
    """Service for authentication-related business logic"""
    
    @staticmethod
    def create_user(db: Database, user_in: UserCreate) -> Dict[str, str]:
        """Create a new user with proper validation"""
        # Check if user already exists by email
        if user_crud.get_by_email(db, email=user_in.email):
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system.",
            )
        
        # Check if user already exists by username
        if user_crud.get_by_username(db, username=user_in.username):
            raise HTTPException(
                status_code=400,
                detail="The user with this username already exists in the system.",
            )
        
        try:
            # Create user
            user = user_crud.create(db, obj_in=user_in)
            
            # Generate and store verification code
            verification_code = AuthService._generate_verification_code()
            verification_codes[user.email] = verification_code
            
            # Send verification email
            try:
                send_verification_email(user.email, verification_code)
            except Exception as e:
                logger.error(f"Failed to send verification email: {e}")
                # Don't fail user creation if email fails
            
            return {
                "message": "User created successfully. Please check your email for verification.",
                "user_id": str(user.id)
            }
            
        except Exception as e:
            # Handle any remaining integrity errors
            if "Duplicate entry" in str(e):
                if "email" in str(e):
                    raise HTTPException(
                        status_code=400,
                        detail="The user with this email already exists in the system.",
                    )
                elif "username" in str(e):
                    raise HTTPException(
                        status_code=400,
                        detail="The user with this username already exists in the system.",
                    )
            raise HTTPException(
                status_code=500,
                detail="Failed to create user.",
            )
    
    @staticmethod
    def authenticate_user(db: Database, user_credentials: UserLogin) -> Dict[str, Any]:
        """Authenticate user and return tokens"""
        user = user_crud.authenticate(
            db, email=user_credentials.email, password=user_credentials.password
        )
        if not user:
            raise HTTPException(
                status_code=400,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        elif not user_crud.is_active(user):
            raise HTTPException(status_code=400, detail="Inactive user")
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Convert user to UserOut format
        user_out = UserOut(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            status=user.status,
            violation_count=user.violation_count,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
        return {
            "access_token": create_access_token(
                data={"user_id": str(user.id)}, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
            "user": user_out
        }
    
    @staticmethod
    def verify_email_code(db: Database, email: str, code: str) -> Dict[str, str]:
        """Verify email with verification code"""
        if email not in verification_codes or verification_codes[email] != code:
            raise HTTPException(
                status_code=400,
                detail="Invalid verification code.",
            )
        
        # Get user and mark as verified
        user = user_crud.get_by_email(db, email=email)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found.",
            )
        
        # Update user as verified
        user_crud.update(db, db_obj=user, obj_in={"is_verified": True})
        
        # Remove verification code
        del verification_codes[email]
        
        return {"message": "Email verified successfully."}
    
    @staticmethod
    def forgot_password(db: Database, email: str) -> Dict[str, str]:
        """Send password reset code to email"""
        user = user_crud.get_by_email(db, email=email)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found.",
            )
        
        # Generate and store reset code
        reset_code = AuthService._generate_verification_code()
        reset_codes[f"reset_{email}"] = reset_code
        
        # Send reset email
        try:
            send_password_reset_email(email, reset_code)
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to send password reset email.",
            )
        
        return {"message": "Password reset code sent to your email."}
    
    @staticmethod
    def reset_password(db: Database, email: str, code: str, new_password: str) -> Dict[str, str]:
        """Reset password with verification code"""
        reset_key = f"reset_{email}"
        if reset_key not in reset_codes or reset_codes[reset_key] != code:
            raise HTTPException(
                status_code=400,
                detail="Invalid reset code.",
            )
        
        # Get user
        user = user_crud.get_by_email(db, email=email)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found.",
            )
        
        # Update password
        user_crud.update(db, db_obj=user, obj_in={"password": new_password})
        
        # Remove reset code
        del reset_codes[reset_key]
        
        return {"message": "Password reset successfully."}
    
    @staticmethod
    def _generate_verification_code() -> str:
        """Generate a 6-digit verification code"""
        import random
        return str(random.randint(100000, 999999)) 