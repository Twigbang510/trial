#!/usr/bin/env python3
"""
Management script for the application
"""
import asyncio
from app.db.session import get_db
from app.crud.crud_user import user_crud
from app.schemas.user import UserCreate

# Import all models to let MongoDB know and create collections
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message

def create_database():
    """Create database collections"""
    print("Creating database collections...")
    # MongoDB collections are created automatically when first document is inserted
    print("✅ Database collections ready")

def create_sample_data():
    """Create sample data for testing"""
    print("Creating sample data...")
    
    # Get database connection
    db = next(get_db())
    
    # Create sample user
    sample_user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpassword123",
        full_name="Test User",
        status="student"
    )
    
    try:
        user = user_crud.create(db, obj_in=sample_user_data)
        print(f"✅ Created sample user: {user.email}")
    except Exception as e:
        print(f"⚠️  Sample user already exists or error: {e}")
    
    print("✅ Sample data creation completed")

def main():
    """Main function"""
    print("🚀 Starting application management...")
    
    # Create database
    create_database()
    
    # Create sample data
    create_sample_data()
    
    print("✅ Application management completed")

if __name__ == "__main__":
    main()
