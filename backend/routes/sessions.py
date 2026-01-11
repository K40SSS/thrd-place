"""
Study session management routes.
Provides endpoints for creating, viewing, joining, and filtering study sessions.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status, Depends, Header, Query
from models import (
    StudySessionCreate,
    StudySessionResponse,
    SessionParticipant
)
from supabase_client import get_supabase_client
from functions.session_functions import (
    create_session,
    get_session_by_id,
    get_user_sessions,
    get_school_sessions,
    add_participant,
    remove_participant,
    get_session_participants,
    delete_session
)
from functions.auth_functions import verify_token

# Create router for session endpoints
router = APIRouter(
    prefix="/sessions",
    tags=["Study Sessions"],
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "Not Found"},
        500: {"description": "Internal Server Error"}
    }
)


def get_current_user(authorization: str = Header(None)):
    """
    Dependency to extract and verify the current user from JWT token in Authorization header.
    
    Expected header format: "Bearer <token>"
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
        
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return user_id
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        )


@router.post("/", response_model=StudySessionResponse, status_code=status.HTTP_201_CREATED)
async def create_new_session(
    session_data: StudySessionCreate,
    user_id: str = Depends(get_current_user),
    db = Depends(get_supabase_client)
) -> StudySessionResponse:
    """
    Create a new study session.
    
    - **title**: Title of the study session (e.g., "CS101 Exam Prep")
    - **course_code**: Course code (e.g., CS101, MATH201)
    - **description**: Detailed description of topics to cover
    - **date**: Session date in YYYY-MM-DD format
    - **time**: Session time in HH:MM format (24-hour)
    - **location**: Physical location or "Online"
    - **meeting_type**: One of "on_campus", "off_campus", or "online"
    - **max_capacity**: Maximum number of participants
    
    Requires authentication via Bearer token.
    """
    return await create_session(db, user_id, session_data)


@router.get("/{session_id}", response_model=StudySessionResponse)
async def get_session(
    session_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_supabase_client)
) -> StudySessionResponse:
    """
    Get details of a specific study session by ID.
    
    Includes current capacity, creator information, and status (full/available).
    Requires authentication via Bearer token.
    """
    return await get_session_by_id(db, session_id)


@router.get("/my/sessions", response_model=List[StudySessionResponse])
async def get_my_sessions(
    user_id: str = Depends(get_current_user),
    db = Depends(get_supabase_client)
) -> List[StudySessionResponse]:
    """
    Get all study sessions for the current user.
    
    Returns both sessions created by the user and sessions they've joined.
    Requires authentication via Bearer token.
    """
    return await get_user_sessions(db, user_id)


@router.get("/", response_model=List[StudySessionResponse])
async def get_available_sessions(
    user_id: str = Depends(get_current_user),
    course_code: str = Query(None, description="Filter by course code"),
    meeting_type: str = Query(None, description="Filter by meeting type: in_person, online, or hybrid"),
    exclude_full: bool = Query(False, description="Exclude sessions that are full"),
    db = Depends(get_supabase_client)
) -> List[StudySessionResponse]:
    """
    Get all available study sessions for the user's school.
    
    Supports filtering by:
    - **course_code**: Show only sessions for a specific course
    - **meeting_type**: Show only in_person, online, or hybrid sessions
    - **exclude_full**: Hide sessions that have reached max capacity
    
    Requires authentication via Bearer token.
    """
    # Get user's school from database
    user_response = db.table('users').select('school').eq('id', user_id).execute()
    if not user_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    school = user_response.data[0]['school']
    
    # Build filters dict
    filters = {}
    if course_code:
        filters['course_code'] = course_code
    if meeting_type:
        filters['meeting_type'] = meeting_type
    if exclude_full:
        filters['exclude_full'] = True
    
    return await get_school_sessions(db, school, filters if filters else None)


@router.post("/{session_id}/join", status_code=status.HTTP_200_OK)
async def join_session(
    session_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_supabase_client)
):
    """
    Join an existing study session.
    
    - **session_id**: ID of the session to join
    
    User must not already be a participant. Session must not be full.
    Requires authentication via Bearer token.
    
    Returns:
        Message confirming successful join
    """
    await add_participant(db, session_id, user_id)
    return {"message": "Successfully joined the session"}


@router.post("/{session_id}/leave", status_code=status.HTTP_200_OK)
async def leave_session(
    session_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_supabase_client)
):
    """
    Leave a study session that you've joined.
    
    - **session_id**: ID of the session to leave
    
    Cannot leave if you're the creator of the session.
    Requires authentication via Bearer token.
    
    Returns:
        Message confirming successful departure
    """
    await remove_participant(db, session_id, user_id)
    return {"message": "Successfully left the session"}


@router.get("/{session_id}/participants", response_model=List[SessionParticipant])
async def get_participants(
    session_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_supabase_client)
) -> List[SessionParticipant]:
    """
    Get all participants in a study session.
    
    - **session_id**: ID of the session
    
    Returns a list of all users participating in the session.
    Requires authentication via Bearer token.
    """
    return await get_session_participants(db, session_id)


@router.delete("/{session_id}")
async def delete_session_endpoint(
    session_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_supabase_client)
):
    """
    Delete a session you created. Only the creator may delete.
    """
    await delete_session(db, session_id, user_id)
    return {"message": "Session deleted"}