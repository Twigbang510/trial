from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserOut, UserLogin
from app.core.security import get_password_hash, verify_password, create_access_token
from app.crud.crud_user import user as user_crud
from app.core.email import generate_verification_code, send_verification_email, store_verification_code, verify_code

router = APIRouter()

@router.post("/signup", response_model=UserOut)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    db_user = user_crud.get_by_email(db, user_data.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user_data.password)
    new_user = UserModel(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/signin")
def signin(form: UserLogin, db: Session = Depends(get_db)):
    db_user = user_crud.get_by_email(db, form.email)
    if not db_user or not verify_password(form.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = create_access_token({"sub": db_user.email, "user_id": db_user.id})
    return {"access_token": access_token, "user": {
        "id": db_user.id,
        "email": db_user.email,
        "username": db_user.username,
        "full_name": db_user.full_name,
        "is_active": db_user.is_active,
        "is_verified": db_user.is_verified
    }}

@router.post("/forgot-password")
def forgot_password(data: dict):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    # Create verification code
    code = generate_verification_code()
    
    # Send email
    if send_verification_email(email, code):
        # Store code for verification
        store_verification_code(email, code)
        return {"msg": f"Verification code sent to {email}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send email")

@router.post("/verify-code")
def verify_verification_code(data: dict):
    email = data.get("email")
    code = data.get("code")
    if not email or not code:
        raise HTTPException(status_code=400, detail="Email and code are required")
    
    if verify_code(email, code):
        return {"msg": "Code verified successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid or expired code")

@router.post("/reset-password")
def reset_password(data: dict, db: Session = Depends(get_db)):
    email = data.get("email")
    new_password = data.get("new_password")
    if not email or not new_password:
        raise HTTPException(status_code=400, detail="Email and new password are required")
    
    # Find user
    db_user = user_crud.get_by_email(db, email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update password
    db_user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return {"msg": "Password reset successfully"} 