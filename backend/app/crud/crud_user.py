# CRUD functions for user (template)
from sqlalchemy.orm import Session
from typing import Optional, Union, Dict, Any
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

class CRUDUser:
    def get(self, db: Session, id: int) -> Optional[User]:
        return db.query(User).filter(User.id == id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def get_list(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(User).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            full_name=obj_in.full_name,
            hashed_password=get_password_hash(obj_in.password),
            is_active=True,
            is_verified=False,
            status=obj_in.status,
            violation_count=0
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
            
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_verified(self, user: User) -> bool:
        return user.is_verified
    
    def increment_violation(self, db: Session, *, user: User, violation_type: str = "WARNING") -> User:
        """
        Increment user's violation count and deactivate if threshold is reached
        
        Args:
            db: Database session
            user: User object
            violation_type: Type of violation ("WARNING" or "BLOCK")
            
        Returns:
            Updated user object
        """
        user.violation_count += 1
        
        # Deactivate user if they have 5 or more violations
        if user.violation_count >= 5:
            user.is_active = False
            
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def reset_violations(self, db: Session, *, user: User) -> User:
        """
        Reset user's violation count (admin function)
        
        Args:
            db: Database session
            user: User object
            
        Returns:
            Updated user object
        """
        user.violation_count = 0
        user.is_active = True
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

user_crud = CRUDUser() 