from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User as UserModel
from app.schemas.user import UserOut, UserUpdate
from app.crud.crud_user import user_crud

router = APIRouter()

@router.get("/", response_model=list[UserOut])
def get_users(db: Session = Depends(get_db)):
    return db.query(UserModel).all()

@router.get("/me", response_model=UserOut)
def read_user_me(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=UserOut)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Update own user.
    """
    user = user_crud.update(db, db_obj=current_user, obj_in=user_in)
    return user 