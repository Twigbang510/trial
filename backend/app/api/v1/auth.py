from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database
from app.api.deps import get_db
from app.schemas.user import UserCreate, UserOut, UserLogin
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/signup", response_model=dict)
def create_user(
    *,
    db: Database = Depends(get_db),
    user_in: UserCreate,
):
    """
    Create new user.
    """
    return AuthService.create_user(db, user_in)

@router.post("/signin")
def login_for_access_token(
    *,
    db: Database = Depends(get_db),
    user_credentials: UserLogin
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    return AuthService.authenticate_user(db, user_credentials)

@router.post("/verify-code")
def verify_email_code(
    *,
    db: Database = Depends(get_db),
    email: str,
    code: str,
):
    """
    Verify email with verification code
    """
    return AuthService.verify_email_code(db, email, code)

@router.post("/forgot-password")
def forgot_password(
    *,
    db: Database = Depends(get_db),
    email: str,
):
    """
    Send password reset code to email
    """
    return AuthService.forgot_password(db, email)

@router.post("/reset-password")
def reset_password(
    *,
    db: Database = Depends(get_db),
    email: str,
    code: str,
    new_password: str,
):
    """
    Reset password with verification code
    """
    return AuthService.reset_password(db, email, code, new_password) 