# Dependency utilities (example: get_db, get_current_user) 
from app.db.session import get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pymongo.database import Database
from app.core.config import settings
from app.core.security import ALGORITHM
from app.crud.crud_user import user_crud
from app.models.user import User
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/signin", auto_error=False)

def get_current_user(
    db: Database = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id_raw: str = payload.get("user_id")
        if user_id_raw is None:
            raise credentials_exception
        user_id: str = str(user_id_raw)
    except (JWTError, ValueError, TypeError):
        raise credentials_exception
    
    user_obj = user_crud.get(db, id=user_id)
    if user_obj is None:
        raise credentials_exception
    return user_obj

def get_current_user_optional(
    db: Database = Depends(get_db), token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id_raw: str = payload.get("user_id")
        if user_id_raw is None:
            return None
        user_id: str = str(user_id_raw)
    except (JWTError, ValueError, TypeError):
        return None
    
    user_obj = user_crud.get(db, id=user_id)
    return user_obj 