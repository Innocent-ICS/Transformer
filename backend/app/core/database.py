"""
Database configuration and connection setup.
Uses Supabase as the backend database for user management.
"""
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Global Supabase client instance
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """
    Get or create the Supabase client instance.
    
    Returns:
        Supabase client instance
        
    Raises:
        ValueError: If Supabase credentials are not configured
    """
    global _supabase_client
    
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError(
                "Supabase credentials not configured. "
                "Please set SUPABASE_URL and SUPABASE_KEY in your .env file"
            )
        
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    return _supabase_client


async def init_database():
    """
    Initialize database tables if they don't exist.
    Creates the users table with proper schema.
    """
    # For Supabase, tables are typically created via the dashboard
    # or SQL migrations. This function can be extended for validation
    pass
