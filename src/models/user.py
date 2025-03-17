"""
User model for HealthData Gateway

This module defines the User model and related functions for authentication,
authorization, and user management.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    """Enumeration of possible user roles"""
    PATIENT = "patient"
    PROVIDER = "provider"
    RESEARCHER = "researcher"
    ADMIN = "admin"

class User(BaseModel):
    """
    User model for HealthData Gateway
    """
    id: str
    email: EmailStr
    full_name: str
    role: UserRole
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    profile: Dict[str, Any] = {}
    
    class Config:
        """Pydantic model configuration"""
        schema_extra = {
            "example": {
                "id": "user123",
                "email": "patient@example.com",
                "full_name": "John Doe",
                "role": "patient",
                "active": True,
                "profile": {
                    "date_of_birth": "1980-01-01",
                    "gender": "male",
                    "address": "123 Main St"
                }
            }
        }

class UserCreate(BaseModel):
    """
    Model for creating a new user
    """
    email: EmailStr
    full_name: str
    password: str
    role: UserRole = UserRole.PATIENT
    profile: Dict[str, Any] = {}

class UserUpdate(BaseModel):
    """
    Model for updating an existing user
    """
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    active: Optional[bool] = None
    profile: Optional[Dict[str, Any]] = None

class UserInDB(User):
    """
    User model with hashed password for database storage
    """
    hashed_password: str

# Create an empty __init__.py file in the models directory to make it a proper package
def get_user_by_id(user_id: str) -> Optional[User]:
    """
    Get a user by ID
    
    In a real implementation, this would query a database.
    This is a placeholder that returns a mock user for development.
    """
    # Mock implementation returning a fake user
    if not user_id:
        return None
        
    mock_user = User(
        id=user_id,
        email=f"{user_id}@example.com",
        full_name=f"User {user_id}",
        role=UserRole.PATIENT,
        profile={
            "date_of_birth": "1980-01-01",
            "gender": "male",
            "address": "123 Main St"
        }
    )
    
    return mock_user

def verify_user_credentials(email: str, password: str) -> Optional[User]:
    """
    Verify user credentials
    
    In a real implementation, this would verify against a database.
    This is a placeholder that returns a mock user for development.
    """
    # Mock implementation for development
    if not email or not password:
        return None
        
    # Extract user ID from email (development only)
    user_id = email.split('@')[0]
    
    mock_user = User(
        id=user_id,
        email=email,
        full_name=f"User {user_id}",
        role=UserRole.PATIENT,
        profile={
            "date_of_birth": "1980-01-01",
            "gender": "male",
            "address": "123 Main St"
        }
    )
    
    return mock_user
