from sqlalchemy.ext.declarative import declarative_base
from typing import Any

Base: Any = declarative_base()

# Import all models here for Alembic
from app.models.conversation import Conversation
from app.models.message import Message