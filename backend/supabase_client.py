"""
Supabase client initialization and connection management.
This module creates and manages the Supabase client used for database operations.
"""

from supabase import create_client, Client
from config import settings

# Initialize Supabase client with credentials from environment variables
# Only initialize if both URL and key are provided
if settings.SUPABASE_URL and settings.SUPABASE_KEY:
    supabase: Client = create_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=settings.SUPABASE_KEY
    )
else:
    supabase: Client = None

def get_supabase_client() -> Client:
    """
    Dependency function to provide Supabase client to routes.
    
    Returns:
        Client: Supabase client instance
    """
    if supabase is None:
        raise RuntimeError(
            "Supabase client not initialized. "
            "Please set SUPABASE_URL and SUPABASE_KEY in your .env file"
        )
    return supabase