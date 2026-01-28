"""
Authentication Dependencies
Provides authentication and authorization for API endpoints
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Get current authenticated user
    For MVP, this is a simplified implementation
    """
    
    # For MVP/demo purposes, return a mock user
    # In production, this would validate JWT tokens and fetch user data
    
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Mock user for demo
    return {
        'id': 'demo_user_123',
        'email': 'demo@marketmind.pro',
        'name': 'Demo User',
        'subscription': 'pro',
        'permissions': ['generate_reports', 'view_reports']
    }

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """Get current user if authenticated, None otherwise"""
    
    if not credentials or not credentials.credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None