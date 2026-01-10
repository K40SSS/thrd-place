"""
Study session business logic functions.
Handles session creation, joining, filtering, and participant management.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from supabase import Client

from models import StudySessionCreate, StudySessionResponse, SessionParticipant


async def create_session(
    db: Client,
    creator_id: str,
    session_data: StudySessionCreate
) -> StudySessionResponse:
    """
    Create a new study session.
    
    Args:
        db: Supabase client
        creator_id: ID of the user creating the session
        session_data: Session details
        
    Returns:
        Created StudySessionResponse
        
    Raises:
        HTTPException: If session creation fails
    """
    try:
        # Get creator information
        creator_response = db.table('users').select('first_name, last_name').eq('id', creator_id).execute()
        if not creator_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        creator = creator_response.data[0]
        now = datetime.utcnow().isoformat()
        
        # Insert session into database
        db_session_data = {
            'title': session_data.title,
            'course_code': session_data.course_code,
            'description': session_data.description,
            'date': session_data.date,
            'time': session_data.time,
            'location': session_data.location,
            'meeting_type': session_data.meeting_type.value,
            'max_capacity': session_data.max_capacity,
            'creator_id': creator_id,
            'created_at': now,
            'updated_at': now
        }
        
        response = db.table('study_sessions').insert(db_session_data).execute()
        session = response.data[0]
        
        # Add creator as first participant
        await add_participant(db, session['id'], creator_id)
        
        return StudySessionResponse(
            id=session['id'],
            title=session['title'],
            course_code=session['course_code'],
            description=session['description'],
            date=session['date'],
            time=session['time'],
            location=session['location'],
            meeting_type=session['meeting_type'],
            max_capacity=session['max_capacity'],
            current_capacity=1,
            creator_id=session['creator_id'],
            creator_name=f"{creator['first_name']} {creator['last_name']}",
            created_at=datetime.fromisoformat(session['created_at']),
            updated_at=datetime.fromisoformat(session['updated_at']),
            is_full=session['max_capacity'] <= 1
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


async def get_session_by_id(db: Client, session_id: str) -> StudySessionResponse:
    """
    Retrieve a study session by ID.
    
    Args:
        db: Supabase client
        session_id: ID of the session
        
    Returns:
        StudySessionResponse
        
    Raises:
        HTTPException: If session not found
    """
    try:
        response = db.table('study_sessions').select('*').eq('id', session_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        session = response.data[0]
        
        # Get creator name
        creator_response = db.table('users').select('first_name, last_name').eq('id', session['creator_id']).execute()
        creator = creator_response.data[0]
        
        # Get current participant count
        participants_response = db.table('session_participants').select('id', count='exact').eq('session_id', session_id).execute()
        current_capacity = len(participants_response.data) if participants_response.data else 0
        
        return StudySessionResponse(
            id=session['id'],
            title=session['title'],
            course_code=session['course_code'],
            description=session['description'],
            date=session['date'],
            time=session['time'],
            location=session['location'],
            meeting_type=session['meeting_type'],
            max_capacity=session['max_capacity'],
            current_capacity=current_capacity,
            creator_id=session['creator_id'],
            creator_name=f"{creator['first_name']} {creator['last_name']}",
            created_at=datetime.fromisoformat(session['created_at']),
            updated_at=datetime.fromisoformat(session['updated_at']),
            is_full=current_capacity >= session['max_capacity']
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve session: {str(e)}"
        )


async def get_user_sessions(db: Client, user_id: str) -> List[StudySessionResponse]:
    """
    Get all sessions for a specific user (both created and joined).
    
    Args:
        db: Supabase client
        user_id: ID of the user
        
    Returns:
        List of StudySessionResponse
    """
    try:
        # Get sessions created by user
        created_response = db.table('study_sessions').select('*').eq('creator_id', user_id).execute()
        created_sessions = created_response.data if created_response.data else []
        
        # Get sessions joined by user
        participated_response = db.table('session_participants').select('session_id').eq('user_id', user_id).execute()
        participated_ids = [p['session_id'] for p in participated_response.data] if participated_response.data else []
        
        sessions = []
        for session_id in participated_ids:
            if session_id not in [s['id'] for s in created_sessions]:
                session_response = await get_session_by_id(db, session_id)
                sessions.append(session_response)
        
        for session_data in created_sessions:
            session_response = await get_session_by_id(db, session_data['id'])
            sessions.append(session_response)
        
        return sessions
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user sessions: {str(e)}"
        )


async def get_school_sessions(db: Client, school: str, filters: Optional[dict] = None) -> List[StudySessionResponse]:
    """
    Get all available sessions for a school with optional filters.
    
    Args:
        db: Supabase client
        school: School name
        filters: Optional filters (course_code, meeting_type, date_from, date_to)
        
    Returns:
        List of StudySessionResponse
    """
    try:
        # Get all users from the school
        users_response = db.table('users').select('id').eq('school', school).execute()
        user_ids = [u['id'] for u in users_response.data] if users_response.data else []
        
        if not user_ids:
            return []
        
        # Get all sessions created by users from this school
        sessions = []
        query = db.table('study_sessions').select('*')
        
        for user_id in user_ids:
            response = query.eq('creator_id', user_id).execute()
            if response.data:
                for session_data in response.data:
                    # Apply filters
                    if filters:
                        if filters.get('course_code') and session_data['course_code'] != filters['course_code']:
                            continue
                        if filters.get('meeting_type') and session_data['meeting_type'] != filters['meeting_type']:
                            continue
                        if filters.get('exclude_full'):
                            participants_response = db.table('session_participants').select('id', count='exact').eq('session_id', session_data['id']).execute()
                            current_capacity = len(participants_response.data) if participants_response.data else 0
                            if current_capacity >= session_data['max_capacity']:
                                continue
                    
                    session_response = await get_session_by_id(db, session_data['id'])
                    sessions.append(session_response)
        
        return sessions
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve school sessions: {str(e)}"
        )


async def add_participant(db: Client, session_id: str, user_id: str) -> None:
    """
    Add a user to a study session.
    
    Args:
        db: Supabase client
        session_id: ID of the session
        user_id: ID of the user to add
        
    Raises:
        HTTPException: If session is full or user already joined
    """
    try:
        # Check if session exists and get details
        session_response = db.table('study_sessions').select('max_capacity').eq('id', session_id).execute()
        if not session_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        session = session_response.data[0]
        
        # Check if user is already a participant
        existing = db.table('session_participants').select('id').eq('session_id', session_id).eq('user_id', user_id).execute()
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already joined this session"
            )
        
        # Check current capacity
        participants = db.table('session_participants').select('id', count='exact').eq('session_id', session_id).execute()
        current_count = len(participants.data) if participants.data else 0
        
        if current_count >= session['max_capacity']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session is full"
            )
        
        # Add participant
        db.table('session_participants').insert({
            'session_id': session_id,
            'user_id': user_id,
            'joined_at': datetime.utcnow().isoformat()
        }).execute()
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to join session: {str(e)}"
        )


async def remove_participant(db: Client, session_id: str, user_id: str) -> None:
    """
    Remove a user from a study session (leave session).
    
    Args:
        db: Supabase client
        session_id: ID of the session
        user_id: ID of the user to remove
        
    Raises:
        HTTPException: If user is not in session or is the creator
    """
    try:
        # Check if user is the creator
        session = db.table('study_sessions').select('creator_id').eq('id', session_id).execute()
        if session.data and session.data[0]['creator_id'] == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Creator cannot leave their own session"
            )
        
        # Remove participant
        db.table('session_participants').delete().eq('session_id', session_id).eq('user_id', user_id).execute()
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to leave session: {str(e)}"
        )


async def get_session_participants(db: Client, session_id: str) -> List[SessionParticipant]:
    """
    Get all participants in a study session.
    
    Args:
        db: Supabase client
        session_id: ID of the session
        
    Returns:
        List of SessionParticipant
    """
    try:
        participants_response = db.table('session_participants').select('user_id, joined_at').eq('session_id', session_id).execute()
        
        participants = []
        for p in participants_response.data if participants_response.data else []:
            user_response = db.table('users').select('id, first_name, last_name, email').eq('id', p['user_id']).execute()
            if user_response.data:
                user = user_response.data[0]
                participants.append(SessionParticipant(
                    id=user['id'],
                    first_name=user['first_name'],
                    last_name=user['last_name'],
                    email=user['email'],
                    joined_at=datetime.fromisoformat(p['joined_at'])
                ))
        
        return participants
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve participants: {str(e)}"
        )
