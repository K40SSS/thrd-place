"""
Group chat functions for study sessions.
Handles message creation, retrieval, and session-based messaging.
"""

from datetime import datetime
from typing import List
from fastapi import HTTPException, status
from supabase import Client

from models import ChatMessageCreate, ChatMessageResponse


async def send_message(
    db: Client,
    user_id: str,
    message_data: ChatMessageCreate
) -> ChatMessageResponse:
    """
    Send a message in a session group chat.
    
    Args:
        db: Supabase client
        user_id: ID of the user sending the message
        message_data: Message content
        
    Returns:
        ChatMessageResponse
        
    Raises:
        HTTPException: If user is not in the session or message fails
    """
    try:
        # Check if user is a participant in the session
        participant_response = db.table('session_participants').select('id').eq('session_id', message_data.session_id).eq('user_id', user_id).execute()
        
        if not participant_response.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a participant in this session"
            )
        
        # Get user information
        user_response = db.table('users').select('first_name, last_name').eq('id', user_id).execute()
        if not user_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user = user_response.data[0]
        now = datetime.utcnow().isoformat()
        
        # Insert message
        message_insert = {
            'session_id': message_data.session_id,
            'user_id': user_id,
            'message': message_data.message,
            'created_at': now
        }
        
        response = db.table('session_messages').insert(message_insert).execute()
        message = response.data[0]
        
        return ChatMessageResponse(
            id=message['id'],
            session_id=message['session_id'],
            user_id=message['user_id'],
            user_name=f"{user['first_name']} {user['last_name']}",
            message=message['message'],
            created_at=datetime.fromisoformat(message['created_at']),
            edited_at=None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


async def get_session_messages(db: Client, session_id: str, limit: int = 50, offset: int = 0) -> List[ChatMessageResponse]:
    """
    Retrieve all messages in a session group chat.
    
    Args:
        db: Supabase client
        session_id: ID of the session
        limit: Maximum number of messages to return
        offset: Number of messages to skip
        
    Returns:
        List of ChatMessageResponse ordered by creation time
    """
    try:
        # Verify session exists
        session_response = db.table('study_sessions').select('id').eq('id', session_id).execute()
        if not session_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Get messages
        messages_response = db.table('session_messages').select('*').eq('session_id', session_id).order('created_at', desc=False).range(offset, offset + limit).execute()
        
        messages = []
        for msg in messages_response.data if messages_response.data else []:
            # Get user name
            user_response = db.table('users').select('first_name, last_name').eq('id', msg['user_id']).execute()
            user = user_response.data[0] if user_response.data else {'first_name': 'Unknown', 'last_name': 'User'}
            
            messages.append(ChatMessageResponse(
                id=msg['id'],
                session_id=msg['session_id'],
                user_id=msg['user_id'],
                user_name=f"{user['first_name']} {user['last_name']}",
                message=msg['message'],
                created_at=datetime.fromisoformat(msg['created_at']),
                edited_at=msg.get('edited_at')
            ))
        
        return messages
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve messages: {str(e)}"
        )


async def delete_message(db: Client, user_id: str, message_id: str) -> None:
    """
    Delete a message (only by the message creator).
    
    Args:
        db: Supabase client
        user_id: ID of the user attempting to delete
        message_id: ID of the message to delete
        
    Raises:
        HTTPException: If user is not the message creator
    """
    try:
        # Get message
        message_response = db.table('session_messages').select('user_id').eq('id', message_id).execute()
        
        if not message_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Check if user is the creator
        if message_response.data[0]['user_id'] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own messages"
            )
        
        # Delete message
        db.table('session_messages').delete().eq('id', message_id).execute()
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete message: {str(e)}"
        )
