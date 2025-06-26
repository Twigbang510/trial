#!/usr/bin/env python3
"""
Database management script
Combines functionality from manage.py and create_tables.py
"""

import os
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

# Import all models to let SQLAlchemy know and create tables
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message

def create_database():
    """Create database if not exists (MySQL only)"""
    url = settings.DATABASE_URL
    if 'mysql' in url:
        import pymysql
        from sqlalchemy.engine.url import make_url
        url_obj = make_url(url)
        db_name = url_obj.database
        url_no_db = url.replace(f"/{db_name}", "")
        engine_no_db = create_engine(url_no_db)
        with engine_no_db.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
        print(f"✅ Database '{db_name}' created (if not exists).")
    else:
        print("❌ Only MySQL is supported for this command.")

def reset_database():
    """Drop all tables and recreate them"""
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("✅ Database reset: All tables dropped and recreated.")
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        return False
    return True

def migrate():
    """Create all tables (if not exists)"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created (if not exists).")
        
        # Verify tables exist
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result]
            print(f"📋 Available tables: {', '.join(tables)}")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

def show_tables():
    """Show all tables in database"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result]
            if tables:
                print("📋 Available tables:")
                for table in tables:
                    print(f"  - {table}")
            else:
                print("📋 No tables found in database.")
    except Exception as e:
        print(f"❌ Error showing tables: {e}")

def show_help():
    """Show help information"""
    print("""
🚀 Database Management Script
============================

Usage: python manage.py [command]

Commands:
  create_db    - Create database if not exists (MySQL only)
  reset_db     - Drop all tables and recreate them
  migrate      - Create all tables (if not exists)
  show_tables  - Show all tables in database
  help         - Show this help message

Examples:
  python manage.py create_db    # Create database
  python manage.py migrate      # Create tables
  python manage.py reset_db     # Reset database
  python manage.py show_tables  # Show tables
""")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ No command specified.")
        show_help()
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    
    if cmd == "create_db":
        print("🚀 Creating database...")
        create_database()
    elif cmd == "reset_db":
        print("🚀 Resetting database...")
        success = reset_database()
        if not success:
            sys.exit(1)
    elif cmd == "migrate":
        print("🚀 Creating tables...")
        success = migrate()
        if not success:
            sys.exit(1)
        print("🎉 Database setup completed!")
    elif cmd == "show_tables":
        show_tables()
    elif cmd == "help":
        show_help()
    else:
        print(f"❌ Unknown command: {cmd}")
        show_help()
        sys.exit(1)
