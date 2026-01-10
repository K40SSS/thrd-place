# Supabase Database Setup Guide

## Quick Setup Instructions

### 1. Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Sign up or log in
3. Create a new project
4. Copy your **Project URL** and **Anon Key**

### 2. Add Credentials to .env
Edit `backend/.env`:
```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_anon_key_here
SECRET_KEY=your_super_secret_key_change_in_production
```

### 3. Create Database Tables
Go to Supabase SQL Editor and run this SQL:

```sql
-- ==================== USERS TABLE ====================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    school VARCHAR(255) NOT NULL,
    bio TEXT,
    rating FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== STUDY SESSIONS TABLE ====================
CREATE TABLE study_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    course_code VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    location VARCHAR(255) NOT NULL,
    meeting_type VARCHAR(50) NOT NULL,
    max_capacity INT NOT NULL,
    creator_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== SESSION PARTICIPANTS TABLE ====================
CREATE TABLE session_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES study_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, user_id)
);

-- ==================== SESSION MESSAGES TABLE ====================
CREATE TABLE session_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES study_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    edited_at TIMESTAMP
);

-- ==================== INDEXES FOR PERFORMANCE ====================
CREATE INDEX idx_study_sessions_creator ON study_sessions(creator_id);
CREATE INDEX idx_study_sessions_course ON study_sessions(course_code);
CREATE INDEX idx_study_sessions_date ON study_sessions(date);
CREATE INDEX idx_session_participants_session ON session_participants(session_id);
CREATE INDEX idx_session_participants_user ON session_participants(user_id);
CREATE INDEX idx_session_messages_session ON session_messages(session_id);
CREATE INDEX idx_session_messages_user ON session_messages(user_id);
CREATE INDEX idx_users_school ON users(school);

-- ==================== ROW LEVEL SECURITY (Optional but Recommended) ====================
-- Enable RLS on tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE study_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_messages ENABLE ROW LEVEL SECURITY;

-- Allow users to read all users (for finding study partners)
CREATE POLICY "Users can read all users" ON users
    FOR SELECT USING (true);

-- Users can read their own data
CREATE POLICY "Users can read own data" ON users
    FOR SELECT USING (auth.uid() = id);

-- Allow users to read sessions from their school
CREATE POLICY "Users can read sessions from their school" ON study_sessions
    FOR SELECT USING (true);

-- Users can create sessions
CREATE POLICY "Users can create sessions" ON study_sessions
    FOR INSERT WITH CHECK (creator_id = auth.uid());

-- Users can update their own sessions
CREATE POLICY "Users can update own sessions" ON study_sessions
    FOR UPDATE USING (creator_id = auth.uid());

-- Anyone can read session participants
CREATE POLICY "Anyone can read participants" ON session_participants
    FOR SELECT USING (true);

-- Users can add themselves as participants
CREATE POLICY "Users can join sessions" ON session_participants
    FOR INSERT WITH CHECK (user_id = auth.uid());

-- Users can remove themselves
CREATE POLICY "Users can leave sessions" ON session_participants
    FOR DELETE USING (user_id = auth.uid());

-- Anyone can read messages
CREATE POLICY "Anyone can read messages" ON session_messages
    FOR SELECT USING (true);

-- Users can send messages
CREATE POLICY "Users can send messages" ON session_messages
    FOR INSERT WITH CHECK (user_id = auth.uid());

-- Users can delete their messages
CREATE POLICY "Users can delete own messages" ON session_messages
    FOR DELETE USING (user_id = auth.uid());
```

### 4. Test the Setup
Run the backend:
```bash
cd backend
python main.py
```

Visit `http://localhost:8000/api/docs` to see the API documentation.

## API Testing with cURL

### Register a User
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.edu",
    "password": "SecurePassword123",
    "first_name": "John",
    "last_name": "Doe",
    "school": "University of Example"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.edu",
    "password": "SecurePassword123"
  }'
```

Response will include an `access_token` - save this for authenticated requests!

### Create a Study Session
```bash
curl -X POST "http://localhost:8000/sessions/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -d '{
    "title": "CS101 Exam Prep",
    "course_code": "CS101",
    "description": "Studying for the midterm exam. Focus on algorithms and data structures.",
    "date": "2026-02-15",
    "time": "14:00",
    "location": "Library Room 305",
    "meeting_type": "in_person",
    "max_capacity": 5
  }'
```

### Get Available Sessions
```bash
curl "http://localhost:8000/sessions/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### Join a Session
```bash
curl -X POST "http://localhost:8000/sessions/{session_id}/join" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### Send a Message
```bash
curl -X POST "http://localhost:8000/chat/{session_id}/messages" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -d '{
    "session_id": "session-uuid",
    "message": "Hey everyone, looking forward to studying together!"
  }'
```

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | `https://abc123.supabase.co` |
| `SUPABASE_KEY` | Supabase anon public key | `eyJhbGci...` |
| `SECRET_KEY` | JWT signing secret | Any long random string |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_HOURS` | Token expiration time | `24` |
| `DEBUG` | Debug mode | `True` or `False` |

## Troubleshooting

### "Invalid URL" Error
- Make sure `SUPABASE_URL` starts with `https://`
- Verify the URL matches your Supabase project URL

### "Invalid Key" Error
- Use the **Anon** key, not the service role key
- Verify the key is complete with no missing characters

### Tables Not Found
- Run the SQL setup in Supabase SQL Editor
- Verify tables exist in Supabase dashboard

### CORS Errors
- Check that `ALLOWED_ORIGINS` in `config.py` includes your frontend URL
- Update if needed in deployment

## Production Deployment

When deploying to production:

1. **Use environment variables from your hosting platform** (don't commit .env)
2. **Set `DEBUG=False`**
3. **Use a strong `SECRET_KEY`** (at least 32 random characters)
4. **Enable Row Level Security (RLS)** in Supabase (SQL provided above)
5. **Use HTTPS only** in production
6. **Keep `SUPABASE_KEY` secret** - use service role key only on backend
7. **Add your production domain to `ALLOWED_ORIGINS`**

## Database Backup

Supabase automatically backs up your data. You can also:
1. Go to Supabase dashboard
2. Project Settings → Backups
3. Download backups manually when needed

## Need Help?

- Supabase Docs: https://supabase.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- Check your Supabase API logs for debugging
