"""
Group chat routes for study sessions.
Provides endpoints for sending and retrieving messages within a session.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status, Depends, Header, Query

from models import ChatMessageCreate, ChatMessageResponse
from supabase_client import get_supabase_client
from functions.chat_functions import send_message, get_session_messages, delete_message
from functions.auth_functions import verify_token

# Create router for chat endpoints
router = APIRouter(
    prefix="/chat",
    tags=["Group Chat"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
        500: {"description": "Internal Server Error"}
    }
)


def get_current_user(authorization: str = Header(None)):
    """
    Dependency to extract and verify the current user from JWT token.
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
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        )


@router.post("/{session_id}/messages", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
async def send_chat_message(
    session_id: str,
    message_data: ChatMessageCreate,
    user_id: str = Depends(get_current_user),
    db = Depends(get_supabase_client)
) -> ChatMessageResponse:
    """
    Send a message in a session group chat.
    
    - **session_id**: ID of the session
    - **message**: Message content (required)
    
    User must be a participant in the session.
    Requires authentication via Bearer token.
    
    Returns the created message with timestamp.
    """
    # Verify session_id matches
    if message_data.session_id != session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session ID mismatch"
        )
    
    return await send_message(db, user_id, message_data)


@router.get("/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_messages(
    session_id: str,
    limit: int = Query(50, ge=1, le=100, description="Number of messages to retrieve"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    user_id: str = Depends(get_current_user),
    db = Depends(get_supabase_client)
) -> List[ChatMessageResponse]:
    """
    Get messages from a session group chat.
    
    - **session_id**: ID of the session
    - **limit**: Maximum number of messages (1-100, default 50)
    - **offset**: Number of messages to skip for pagination
    
    Returns messages ordered by creation time (oldest first).
    Requires authentication via Bearer token.
    """
    return await get_session_messages(db, session_id, limit, offset)


@router.delete("/messages/{message_id}", status_code=status.HTTP_200_OK)
async def delete_chat_message(
    message_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_supabase_client)
):
    """
    Delete a message from the group chat.
    
    - **message_id**: ID of the message to delete
    
    Only the message creator can delete their messages.
    Requires authentication via Bearer token.
    
    Returns:
        Message confirming successful deletion
    """
    await delete_message(db, user_id, message_id)
    return {"message": "Message deleted successfully"}
