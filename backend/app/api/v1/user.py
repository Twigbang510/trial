from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database
from typing import List, Optional
from app.api.deps import get_db, get_current_user
from app.models.user import User as UserModel
from app.schemas.user import UserOut, UserUpdate
from app.crud.crud_user import user_crud
from app.crud.crud_lecturer_availability import lecturer_availability

router = APIRouter()

@router.get("/", response_model=list[UserOut])
def get_users(db: Database = Depends(get_db)):
    users = user_crud.get_list(db, limit=100)
    return [UserOut(**user.model_dump()) for user in users]

@router.get("/me", response_model=UserOut)
def read_user_me(
    db: Database = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Get current user.
    """
    return UserOut(**current_user.model_dump())

@router.put("/me", response_model=UserOut)
def update_user_me(
    *,
    db: Database = Depends(get_db),
    user_in: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Update own user.
    """
    user = user_crud.update(db, db_obj=current_user, obj_in=user_in)
    return UserOut(**user.model_dump())

@router.get("/me/bookings")
def get_my_bookings(
    *,
    db: Database = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    status: Optional[str] = None,
    limit: int = 50
):
    """
    Get current user's bookings.
    """
    status_filter = None
    if status:
        status_filter = [status]
    
    bookings = lecturer_availability.get_user_bookings(
        db=db, 
        user_id=str(current_user.id), 
        status_filter=status_filter,
        limit=limit
    )
    
    return {
        "bookings": bookings,
        "total": len(bookings)
    } 