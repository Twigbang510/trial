from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import Field, EmailStr, ConfigDict
from app.db.base import BaseDocument, PyObjectId

class UserStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SCHEDULED = "SCHEDULED"

class User(BaseDocument):
    email: EmailStr = Field(..., description="User email address")
    username: Optional[str] = Field(None, max_length=64, description="Username")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")
    hashed_password: str = Field(..., max_length=255, description="Hashed password")
    is_active: bool = Field(default=True, description="User active status")
    is_verified: bool = Field(default=False, description="Email verification status")
    status: UserStatus = Field(default=UserStatus.PENDING, description="User status")
    violation_count: int = Field(default=0, description="Number of violations")
    
    model_config = ConfigDict(
        collection_name="users",
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "username": "username",
                "full_name": "Full Name",
                "hashed_password": "hashed_password",
                "is_active": True,
                "is_verified": False,
                "status": "PENDING",
                "violation_count": 0
            }
        }
    )
    
    def to_dict(self) -> dict:
        """Convert to dictionary with string IDs"""
        data = self.model_dump()
        data["id"] = str(self.id)
        return data 