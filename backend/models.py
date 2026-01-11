"""
Pydantic models for request/response validation and database schema representation.
These models ensure type safety and automatic validation for all API endpoints.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


# ==================== AUTHENTICATION MODELS ====================

class MeetingType(str, Enum):
    """Enum for different meeting types"""
    ON_CAMPUS = "on_campus"
    OFF_CAMPUS = "off_campus"
    ONLINE = "online"


class RegisterRequest(BaseModel):
    """
    User registration request model.
    Validates data when a new user signs up with school email.
    """
    email: EmailStr = Field(..., description="School email address")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    school: str = Field(..., description="Name of the school/university")


class LoginRequest(BaseModel):
    """
    User login request model.
    Validates credentials during login.
    """
    email: EmailStr = Field(..., description="School email address")
    password: str = Field(..., description="Password")


class AuthResponse(BaseModel):
    """
    Authentication response model.
    Returned after successful login or registration.
    """
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User's email")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    school: str = Field(..., description="User's school")
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


# ==================== USER MODELS ====================

class UserProfile(BaseModel):
    """
    User profile model representing a user in the system.
    """
    id: str
    email: str
    first_name: str
    last_name: str
    school: str
    created_at: datetime
    bio: Optional[str] = None
    rating: Optional[float] = None  # Average rating from study session reviews


class UserUpdate(BaseModel):
    """
    Model for updating user profile information.
    """
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None


# ==================== STUDY SESSION MODELS ====================

class StudySessionCreate(BaseModel):
    """
    Model for creating a new study session.
    Contains all required information for a study session posting.
    """
    title: str = Field(..., description="Session title")
    course_code: str = Field(..., description="Course code (e.g., CS101, MATH201)")
    description: str = Field(..., description="Detailed description of what will be studied")
    date: str = Field(..., description="Date of the session (ISO format: YYYY-MM-DD)")
    time: str = Field(..., description="Time of the session (ISO format: HH:MM)")
    location: str = Field(..., description="Physical location or 'Online'")
    meeting_type: MeetingType = Field(..., description="Type of meeting: in_person, online, or hybrid")
    max_capacity: int = Field(..., gt=0, description="Maximum number of participants")


class StudySessionUpdate(BaseModel):
    """
    Model for updating an existing study session.
    All fields are optional to allow partial updates.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    location: Optional[str] = None
    meeting_type: Optional[MeetingType] = None
    max_capacity: Optional[int] = None


class StudySessionResponse(BaseModel):
    """
    Complete study session response model.
    Includes session details and participant information.
    """
    id: str = Field(..., description="Session ID")
    title: str
    course_code: str
    description: str
    date: str
    time: str
    location: str
    meeting_type: MeetingType
    max_capacity: int
    current_capacity: int = Field(..., description="Current number of participants")
    creator_id: str = Field(..., description="ID of the user who created the session")
    creator_name: str = Field(..., description="Name of the creator")
    created_at: datetime
    updated_at: datetime
    is_full: bool = Field(..., description="Whether the session has reached max capacity")


# ==================== PARTICIPANT MODELS ====================

class SessionParticipant(BaseModel):
    """
    Model representing a user participating in a study session.
    """
    id: str = Field(..., description="Participant user ID")
    first_name: str
    last_name: str
    email: str
    joined_at: datetime


class JoinSessionRequest(BaseModel):
    """
    Request model for joining a study session.
    """
    session_id: str = Field(..., description="ID of the session to join")


# ==================== CHAT MESSAGE MODELS ====================

class ChatMessageCreate(BaseModel):
    """
    Model for creating a new chat message in a session group chat.
    """
    session_id: str = Field(..., description="ID of the session")
    message: str = Field(..., min_length=1, description="Message content")


class ChatMessageResponse(BaseModel):
    """
    Complete chat message response model.
    """
    id: str = Field(..., description="Message ID")
    session_id: str
    user_id: str
    user_name: str = Field(..., description="Name of the user who sent the message")
    message: str
    created_at: datetime
    edited_at: Optional[datetime] = None


# ==================== FILTER MODELS ====================

class SessionFilterRequest(BaseModel):
    """
    Model for filtering study sessions.
    Used to search sessions by various criteria.
    """
    course_code: Optional[str] = None
    meeting_type: Optional[MeetingType] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    search_term: Optional[str] = None  # Search in title and description
    exclude_full: bool = Field(default=False, description="Exclude full sessions")


# ==================== REVIEW MODELS (Future AI Feature) ====================

class ReviewCreate(BaseModel):
    """
    Model for creating a study mate review.
    Future feature for AI-generated user descriptions.
    """
    reviewed_user_id: str = Field(..., description="ID of the user being reviewed")
    session_id: str = Field(..., description="ID of the session this review is for")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: str = Field(..., description="Review comment")


class ReviewResponse(BaseModel):
    """
    Complete review response model.
    """
    id: str
    reviewed_user_id: str
    reviewer_user_id: str
    session_id: str
    rating: int
    comment: str
    ai_generated_description: Optional[str] = None  # Auto-generated after reviews
    created_at: datetime