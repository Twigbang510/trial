# Trial WebApp Backend

A FastAPI backend application with authentication, chatbot functionality using Google Gemini AI, and MySQL database.

## Features

- 🔐 **Authentication System**: JWT-based auth with signup, signin, forgot password, reset password
- 🤖 **AI Chatbot**: Google Gemini AI integration with conversation storage
- 📧 **Email Service**: SMTP email for password reset and verification
- 💾 **Database**: MySQL with SQLAlchemy ORM
- 🛡️ **Security**: Password hashing, JWT tokens, CORS protection

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the backend directory:

```env
# Project Configuration
PROJECT_NAME=Trial WebApp
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/database_name

# Email Configuration (Gmail SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com

# Gemini AI Configuration
GEMINI_API_KEY=your-gemini-api-key-here
```

### 3. Database Setup
```bash
# Create database and tables
python manage.py create_db
python manage.py migrate

# Show tables
python manage.py show_tables

# Reset database (if needed)
python manage.py reset_db
```

### 4. Run Server
```bash
# Development
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the npm script from frontend
npm run start:backend
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/signup` - User registration
- `POST /api/v1/auth/signin` - User login
- `POST /api/v1/auth/forgot-password` - Request password reset
- `POST /api/v1/auth/verify-code` - Verify reset code
- `POST /api/v1/auth/reset-password` - Reset password

### Chatbot
- `POST /api/v1/chatbot/chat` - Send message to AI
- `GET /api/v1/chatbot/conversations` - Get user conversations
- `GET /api/v1/chatbot/conversations/{id}` - Get conversation details
- `DELETE /api/v1/chatbot/conversations/{id}` - Delete conversation

### Users
- `GET /api/v1/users/` - Get all users

## Database Management

Use the `manage.py` script for database operations:

```bash
# Show help
python manage.py help

# Create database
python manage.py create_db

# Create tables
python manage.py migrate

# Reset database
python manage.py reset_db

# Show tables
python manage.py show_tables
```

## Environment Setup

### Gmail SMTP Setup
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password: Account Settings → Security → App Passwords
3. Use the app password in `SMTP_PASSWORD`

### Gemini AI Setup
1. Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add the key to `GEMINI_API_KEY`

### MySQL Setup
1. Install MySQL server
2. Create a database
3. Update `DATABASE_URL` with your credentials

## Development

### File Structure
```
backend/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Core functionality (config, security, etc.)
│   ├── crud/            # Database operations
│   ├── db/              # Database configuration
│   ├── models/          # SQLAlchemy models
│   └── schemas/         # Pydantic schemas
├── manage.py            # Database management script
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Adding New Features
1. Create models in `app/models/`
2. Create schemas in `app/schemas/`
3. Create CRUD operations in `app/crud/`
4. Create API endpoints in `app/api/v1/`
5. Update `app/main.py` to include new routers