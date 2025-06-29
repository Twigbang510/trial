# Trial WebApp Backend - Technical Specification

## 1. TỔNG QUAN HỆ THỐNG

### 1.1 Mô tả dự án
Trial WebApp Backend là hệ thống API RESTful xây dựng trên FastAPI, cung cấp dịch vụ backend cho ứng dụng tư vấn giáo dục tích hợp AI. Hệ thống bao gồm các module: authentication, AI chatbot, content moderation, user management.

### 1.2 Kiến trúc tổng thể
```
Frontend (React) ↔ Backend API (FastAPI) ↔ Database (MySQL)
                           ↓
                External APIs (Gemini, OpenAI, SMTP)
```

### 1.3 Tech Stack
- **Framework**: FastAPI + SQLAlchemy ORM
- **Database**: MySQL
- **Authentication**: JWT tokens
- **AI**: Google Gemini API 2.0-flash
- **Moderation**: OpenAI Moderation API
- **Email**: SMTP service

## 2. DATABASE SCHEMA

### 2.1 Core Tables
**Users Table:**
- id, username, email, full_name, hashed_password
- is_active, is_verified, violation_count
- created_at, updated_at

**Conversations Table:**
- id, user_id, title, context (consultant/booking_assistant)
- Foreign key relationship với Users

**Messages Table:**
- id, conversation_id, content, sender (user/bot), is_appropriate
- Foreign key relationship với Conversations

## 3. API ENDPOINTS

### 3.1 Authentication APIs

#### POST /api/v1/auth/signup
**Xử lý Registration:**
1. Validate input data (email/username uniqueness)
2. Hash password với bcrypt
3. Create user record (is_verified=False)
4. Generate 6-digit verification code
5. Send verification email via SMTP
6. Return success message

#### POST /api/v1/auth/signin
**Xử lý Login:**
1. Validate email format và retrieve user
2. Verify password với bcrypt
3. Check user is_active status
4. Generate JWT token (8 days expiry)
5. Return token + user info

#### POST /api/v1/auth/verify-code
**Xử lý Email Verification:**
1. Validate verification code từ memory cache
2. Update user is_verified=True
3. Remove verification code
4. Return success confirmation

### 3.2 Chatbot APIs

#### POST /api/v1/chatbot/chat
**Xử lý AI Conversation:**

**Bước 1: Kiểm tra tin nhắn rác (Fail-fast validation)**

Bước 1.1: Kiểm tra tin nhắn trống
- Mục đích: Nếu người dùng gửi tin nhắn rỗng hoặc chỉ chứa khoảng trắng → kết thúc sớm
- Logic: Check `not message or not message.strip()`
- Kết quả: Trả về status "EMPTY" với thông báo nhập tin nhắn

Bước 1.2: Kiểm tra emoji-only
- Mục đích: Nếu người dùng chỉ gửi emoji (ví dụ: "👍😅") thì không cần xử lý logic phức tạp
- Logic: Remove tất cả non-alphanumeric characters, check if empty
- Kết quả: Trả về status "EMOJI_ONLY" với yêu cầu gửi text

Bước 1.3: Kiểm tra tin nhắn quá ngắn
- Mục đích: Tin nhắn < 3 ký tự có thể không có ý nghĩa
- Logic: Check `len(message.strip()) < 3`
- Kết quả: Trả về status "TOO_SHORT" với yêu cầu chi tiết hơn

Bước 1.4: Kiểm tra spam pattern
- Mục đích: Phát hiện repeated characters (aaaaaaa)
- Logic: Regex pattern `(.)\1{5,}` để detect repetition
- Kết quả: Trả về status "SPAM_PATTERN" với yêu cầu tin nhắn rõ ràng

**Bước 2: Content Moderation**
1. Gọi OpenAI Moderation API với user message
2. Tính toán harmful_score (max của category scores)
3. Classification: CLEAN/WARNING/BLOCK dựa trên threshold
4. Handle violations: increment user violation_count, suspend account nếu cần

**Bước 3: AI Processing**
1. Quản lý conversation (create new hoặc get existing)
2. Lưu user message vào database
3. Retrieve conversation history cho context
4. Gọi Google Gemini API với appropriate system prompt
5. Lưu AI response vào database
6. Update conversation title nếu là message đầu tiên
7. Return formatted response với moderation info

#### GET /api/v1/chatbot/conversations
**Xử lý Conversation List:**
1. Authenticate user từ JWT token
2. Check account active status
3. Query conversations belong to user với pagination
4. Return list với title, context, timestamps

#### DELETE /api/v1/chatbot/conversations/{id}
**Xử lý Delete Conversation:**
1. Verify user ownership của conversation
2. Cascade delete tất cả messages
3. Return success confirmation

## 4. CONTENT MODERATION SYSTEM

### 4.1 Fail-fast Validation Pipeline
**Validation Order:** Empty → Emoji-only → Too Short → Spam Pattern → Full Moderation

**Performance Benefits:**
- Reduce API calls cho obvious invalid messages
- Improve response time với early returns
- Better user experience với immediate feedback

### 4.2 OpenAI Moderation Integration
**Process Flow:**
1. Send text đến OpenAI Moderation endpoint
2. Parse response categories và scores
3. Calculate overall harmful_score
4. Apply business rules cho classification
5. Handle graceful fallback nếu API fails

### 4.3 Violation Handling System
**Progressive Penalties:**
- WARNING: +1 violation count
- BLOCK: +2 violation count
- Account suspension at 5 violations
- Comprehensive logging cho audit trail

## 5. AI INTEGRATION

### 5.1 Google Gemini Configuration
**Model Setup:** gemini-2.0-flash với API key authentication

### 5.2 Context-based System Prompts
**Consultant Context:** Professional career và education advisor role
**Booking Assistant Context:** Scheduling và appointment focus
**Default Context:** General helpful assistant

### 5.3 Conversation Flow Management
**History Handling:**
- Format previous messages cho Gemini API
- Maintain conversation context across multiple turns
- Handle new conversations vs continuing existing ones
- Error fallback với graceful degradation

## 6. SECURITY IMPLEMENTATION

### 6.1 Authentication Security
- JWT tokens với configurable expiration
- Bcrypt password hashing với salt
- Email verification required cho account activation
- Account suspension mechanism cho policy violations

### 6.2 API Security Measures
- Input validation với Pydantic schemas
- SQL injection prevention với ORM
- CORS configuration cho specific origins
- Rate limiting capabilities (future implementation)

### 6.3 Content Security Framework
- Multi-layer content moderation (fail-fast + AI)
- Progressive user penalties
- Comprehensive audit logging
- Real-time violation tracking

## 7. SYSTEM CONFIGURATION

### 7.1 Environment Variables
**Core Settings:** PROJECT_NAME, SECRET_KEY, DATABASE_URL
**Email Service:** SMTP_SERVER, SMTP_PORT, credentials
**AI Services:** GEMINI_API_KEY, OPENAI_API_KEY
**Thresholds:** MODERATION_HARMFUL_THRESHOLD (default: 0.7)

### 7.2 Database Management
**CLI Operations:**
- `create_db`: Initialize database
- `migrate`: Create/update tables
- `reset_db`: Full database reset
- `show_tables`: List current schema

## 8. MONITORING VÀ PERFORMANCE

### 8.1 Logging Strategy
**Categories:**
- Authentication events (login/logout/failures)
- Content moderation results và violations
- API errors với stack traces
- Performance metrics (response times)
- External API latencies

### 8.2 Error Handling Framework
**Consistent Response Format:**
- Structured error messages
- HTTP status codes
- Error categorization
- User-friendly fallbacks

### 8.3 Performance Considerations
**Optimization Areas:**
- Database query performance
- External API call efficiency
- Fail-fast validation benefits
- Memory usage optimization
- Response time monitoring 