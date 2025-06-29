from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.api.deps import get_db
from app.core.config import settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.crud.crud_user import user_crud
from app.schemas.user import UserCreate, UserOut, UserLogin
from app.core.email import send_verification_email
import random
import string

router = APIRouter()

# Store verification codes temporarily (in production, use Redis or database)
verification_codes = {}

@router.post("/signup", response_model=dict)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
):
    """
    Create new user.
    """
    # Check if user already exists
    if user_crud.get_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    
    # Create user
    user = user_crud.create(db, obj_in=user_in)
    
    # Generate verification code
    verification_code = ''.join(random.choices(string.digits, k=6))
    verification_codes[user.email] = verification_code
    
    # Send verification email
    try:
        send_verification_email(user.email, verification_code)
    except Exception as e:
        print(f"Failed to send verification email: {e}")
    
    return {"message": "User created successfully. Please check your email for verification code."}

@router.post("/signin")
def login_for_access_token(
    *,
    db: Session = Depends(get_db),
    user_credentials: UserLogin
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = user_crud.authenticate(
        db, email=user_credentials.email, password=user_credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user_crud.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Convert user to UserOut format
    user_out = UserOut.from_orm(user)
    
    return {
        "access_token": create_access_token(
            data={"user_id": user.id}, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "user": user_out,
    }

@router.post("/verify-code")
def verify_email_code(
    *,
    db: Session = Depends(get_db),
    email: str,
    code: str,
):
    """
    Verify email with verification code
    """
    if email not in verification_codes or verification_codes[email] != code:
        raise HTTPException(
            status_code=400,
            detail="Invalid verification code"
        )
    
    # Get user and mark as verified
    user = user_crud.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Update user as verified
    user_crud.update(db, db_obj=user, obj_in={"is_verified": True})
    
    # Remove verification code
    del verification_codes[email]
    
    return {"message": "Email verified successfully"}

@router.post("/forgot-password")
def forgot_password(
    *,
    db: Session = Depends(get_db),
    email: str,
):
    """
    Send password reset code to email
    """
    user = user_crud.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User with this email does not exist"
        )
    
    # Generate reset code
    reset_code = ''.join(random.choices(string.digits, k=6))
    verification_codes[f"reset_{email}"] = reset_code
    
    # Send reset email
    try:
        send_verification_email(email, reset_code, is_reset=True)
    except Exception as e:
        print(f"Failed to send reset email: {e}")
    
    return {"message": "Password reset code sent to your email"}

@router.post("/reset-password")
def reset_password(
    *,
    db: Session = Depends(get_db),
    email: str,
    code: str,
    new_password: str,
):
    """
    Reset password with verification code
    """
    reset_key = f"reset_{email}"
    if reset_key not in verification_codes or verification_codes[reset_key] != code:
        raise HTTPException(
            status_code=400,
            detail="Invalid reset code"
        )
    
    # Get user
    user = user_crud.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Update password
    user_crud.update(db, db_obj=user, obj_in={"password": new_password})
    
    # Remove reset code
    del verification_codes[reset_key]
    
    return {"message": "Password reset successfully"} 