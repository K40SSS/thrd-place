# Third Place

A web platform connecting students for collaborative study sessions through real-time group chat, course-specific matching, and session coordination.

## Overview

Third Place addresses the challenge of finding study partners by creating a dedicated space for students to organize, join, and coordinate study sessions. Students can browse available sessions by course code, join group chats, and collaborate effectively.

## Features

- School email authentication (.edu, .ac.uk domains)
- Create and browse study sessions by course, date, and meeting type
- Real-time group chat for active sessions
- Session capacity management
- Advanced search and filtering
- Participant tracking

## Tech Stack

**Backend**
- FastAPI (Python)
- Supabase (PostgreSQL)
- JWT Authentication
- Bcrypt password hashing

**Frontend**
- Vanilla JavaScript
- HTML5/CSS3
- Polling-based real-time updates

## Quick Start

### Prerequisites
- Python 3.9+
- Supabase account (free tier available)

### Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure Environment**

Create `backend/.env`:
```
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_anon_key
SECRET_KEY=your_random_secret_key
```

3. **Setup Database**

Run the SQL from [SETUP.md](SETUP.md) in your Supabase SQL Editor.

4. **Start Backend**
```bash
cd backend
python main.py
```

Backend runs at `http://localhost:8000`

5. **Start Frontend**

Open `frontend/index.html` in your browser or use a local server:
```bash
python -m http.server 3000
```

## API Documentation

Interactive API docs available at `http://localhost:8000/api/docs` when backend is running.

### Key Endpoints

**Authentication**
- `POST /auth/register` - Create account
- `POST /auth/login` - Login with JWT

**Sessions**
- `POST /sessions/` - Create study session
- `GET /sessions/` - Browse sessions with filters
- `POST /sessions/{id}/join` - Join session
- `GET /sessions/my/sessions` - Get user's sessions

**Chat**
- `POST /chat/{session_id}/messages` - Send message
- `GET /chat/{session_id}/messages` - Get chat history

## Project Structure

```
deltahacks/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── models.py            # Pydantic models
│   ├── supabase_client.py   # Database client
│   ├── functions/           # Business logic
│   │   ├── auth_functions.py
│   │   ├── session_functions.py
│   │   └── chat_functions.py
│   └── routes/              # API endpoints
│       ├── auth_route.py
│       ├── sessions.py
│       └── chat_route.py
├── frontend/
│   ├── templates/           # HTML pages
│   ├── Scripts/             # JavaScript
│   ├── Styles/              # CSS
│   └── Icons/               # Images
├── requirements.txt
└── SETUP.md                 # Database setup guide
```

## Contributing

This project was built for DeltaHacks. For setup issues, refer to [SETUP.md](SETUP.md).

## License

MIT
