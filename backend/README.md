# StudyMate Backend Documentation

A FastAPI backend for StudyMate - a platform where students create accounts with school email, post study sessions, join them with capacity limits, and communicate via group chat.

---

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Python 3.9+
- Supabase account (free at https://supabase.com)

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Supabase
1. Create a Supabase project at https://supabase.com
2. In your Supabase dashboard, go to **Settings** → **API Keys**
3. Copy your `Project URL` and `anon key`
4. Update `.env` file in the backend folder:
   ```
   SUPABASE_URL=your_project_url_here
   SUPABASE_KEY=your_anon_key_here
   SECRET_KEY=your_random_secret_key_here
   ```

### 3. Setup Database
1. In Supabase, go to **SQL Editor** → **New Query**
2. Copy and paste the entire SQL from `SUPABASE_SETUP.md`
3. Click **Run**

### 4. Start the Backend
```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

✅ Backend is running!

---

## 📚 API Documentation

### View Interactive Docs
Open your browser to: **http://localhost:8000/api/docs**

This shows all endpoints with live testing capabilities!

---

## 🔐 Authentication

All protected endpoints require a Bearer token. Here's how it works:

### 1. Register a User
```bash
POST http://localhost:8000/auth/register
Content-Type: application/json

{
  "email": "student@university.edu",
  "password": "SecurePassword123",
  "first_name": "John",
  "last_name": "Doe",
  "school": "University Name"
}
```

Response:
```json
{
  "user_id": "abc123",
  "email": "student@university.edu",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer"
}
```

### 2. Login
```bash
POST http://localhost:8000/auth/login
Content-Type: application/json

{
  "email": "student@university.edu",
  "password": "SecurePassword123"
}
```

### 3. Use Token in Requests
Copy the `token` from the response above, then use it in the `Authorization` header:

```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 📖 Common API Endpoints

### Create a Study Session
```bash
POST http://localhost:8000/sessions/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "title": "Calculus Study Group",
  "course_code": "MATH-101",
  "description": "Let's study for midterms together!",
  "date": "2024-01-15",
  "time": "14:30",
  "location": "Library Room 203",
  "meeting_type": "in_person",
  "max_capacity": 5
}
```

### List All Sessions
```bash
GET http://localhost:8000/sessions/?course_code=MATH-101
Authorization: Bearer YOUR_TOKEN
```

### Get Specific Session
```bash
GET http://localhost:8000/sessions/session-id-here
Authorization: Bearer YOUR_TOKEN
```

### Join a Session
```bash
POST http://localhost:8000/sessions/session-id-here/join
Authorization: Bearer YOUR_TOKEN
```

### Leave a Session
```bash
POST http://localhost:8000/sessions/session-id-here/leave
Authorization: Bearer YOUR_TOKEN
```

### Send Message in Session Chat
```bash
POST http://localhost:8000/chat/session-id-here/messages
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "message": "See you in 5 minutes!"
}
```

### Get Messages from Session
```bash
GET http://localhost:8000/chat/session-id-here/messages?limit=50
Authorization: Bearer YOUR_TOKEN
```

---

## 📂 Project Structure

```
backend/
├── main.py                    # Starts the FastAPI server
├── config.py                  # Loads environment variables
├── models.py                  # Data validation (Pydantic)
├── supabase_client.py         # Database connection
├── requirements.txt           # Python packages to install
├── .env                       # Your Supabase credentials (CREATE THIS)
│
├── functions/                 # Business logic (no HTTP, just Python)
│   ├── auth_functions.py      # User registration, login, password hashing
│   ├── session_functions.py   # Create, list, join sessions
│   └── chat_functions.py      # Send/receive messages
│
└── routes/                    # HTTP endpoints (what the frontend calls)
    ├── auth_route.py          # /auth/register, /auth/login
    ├── sessions.py            # /sessions/* endpoints
    └── chat_route.py          # /chat/* endpoints
```

**Why split functions and routes?**
- **functions/** = pure Python logic (testable, reusable)
- **routes/** = HTTP layer (converts requests to function calls)

---

## 🛠️ For Frontend Developers

### Understanding the Response Format

All successful responses have this structure:
```json
{
  "data": {...},        // Your actual data
  "status": "success",
  "message": "Operation completed"
}
```

Error responses:
```json
{
  "detail": "Email already registered"
}
```

### Testing Endpoints

#### Option 1: Swagger UI (Easiest!)
1. Start backend: `python main.py`
2. Open http://localhost:8000/api/docs
3. Click "Authorize" button, paste your token
4. Click any endpoint → "Try it out" → fill in values → "Execute"

#### Option 2: Using cURL (Command Line)
```bash
curl -X GET http://localhost:8000/sessions/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Option 3: Using Postman
1. Download Postman: https://www.postman.com
2. Create new request → set method to GET/POST
3. URL: http://localhost:8000/sessions/
4. Headers tab → Add `Authorization: Bearer YOUR_TOKEN`
5. Click Send

---

## ❓ Common Questions

### Q: "My token isn't working"
**A:** Tokens expire after 24 hours. Log in again to get a new one.

### Q: "Session creation is failing"
**A:** Make sure:
- You're logged in (have a valid token)
- Date format is `YYYY-MM-DD`
- Time format is `HH:MM` (24-hour)
- meeting_type is one of: `in_person`, `online`, `hybrid`

### Q: "I get 'Supabase connection error'"
**A:** Check your `.env` file:
- Is `SUPABASE_URL` correct? (Should start with `https://`)
- Is `SUPABASE_KEY` correct?
- Did you run the SQL setup in Supabase?

### Q: "How do I debug?"
**A:** Check the terminal where you ran `python main.py` - all errors are printed there!

---

## 📝 Environment Variables Explained

Create a `.env` file in the backend folder with:

```
# Your Supabase project details
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-public-key-from-supabase

# Random secret for token signing (can be any long string)
SECRET_KEY=your-super-secret-key-change-this-to-something-random

# JWT Configuration (don't change these)
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24

# CORS (allow frontend to connect)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:5500

# Debug mode (set to False in production)
DEBUG=True
```

---

## 🧪 Testing Your Backend

### Test 1: Is it running?
```bash
curl http://localhost:8000/auth/health
```

Should return `{"message": "Backend is healthy"}`

### Test 2: Register a user
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@university.edu",
    "password": "Test123456!",
    "first_name": "Test",
    "last_name": "User",
    "school": "Test University"
  }'
```

### Test 3: Login and get token
Copy the token from registration, then test authentication with it.

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'fastapi'` | Run `pip install -r requirements.txt` |
| `Connection refused` on Supabase | Check `.env` file - URL and KEY must be correct |
| `Port 8000 already in use` | Kill the other process or use `python main.py --port 8001` |
| `Unauthorized` error | Check your token - it expires after 24 hours |
| `CORS error in browser` | Add your frontend URL to `ALLOWED_ORIGINS` in `.env` |

---

## 📚 Additional Resources

- **Swagger UI**: http://localhost:8000/api/docs (when backend is running)
- **Supabase Docs**: https://supabase.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQL Setup**: See `SUPABASE_SETUP.md` in this folder

---

## ✅ Checklist

Before asking the backend developer for help:

- [ ] Python 3.9+ installed
- [ ] `pip install -r requirements.txt` ran successfully
- [ ] `.env` file created with Supabase credentials
- [ ] SQL setup script ran in Supabase
- [ ] `python main.py` starts without errors
- [ ] Can access http://localhost:8000/api/docs
- [ ] Can register a user via Swagger UI
- [ ] Can login and get a token
- [ ] Can create a session with token

---

## 🆘 Need Help?

1. **Check the logs**: Look at the terminal where `python main.py` is running
2. **Visit Swagger UI**: http://localhost:8000/api/docs - shows what's expected
3. **Check `.env`**: Make sure Supabase credentials are correct
4. **Test endpoint**: Try the endpoint in Swagger UI first before adding to frontend

---

**Last Updated**: January 2026 | **Framework**: FastAPI 0.128.0 | **Database**: Supabase (PostgreSQL)
