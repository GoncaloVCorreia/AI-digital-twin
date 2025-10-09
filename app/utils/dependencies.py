"""
FastAPI dependency functions.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.interviewers import User
from app.services.interviewers_service import AuthService
from app.utils.security import verify_token

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        username = verify_token(credentials.credentials)
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    
    user = AuthService.get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def get_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current admin user."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Resource-based permissions
class RequirePermission:
    """Dependency class for resource-based permissions."""
    
    def __init__(self, resource: str, action: str):
        self.resource = resource
        self.action = action
    
    def __call__(
        self, 
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> User:
        """Check if user has permission for resource action."""
        # Implement permission checking logic here
        # This is a simplified example
        if not self._user_has_permission(current_user, self.resource, self.action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions to {self.action} {self.resource}"
            )
        return current_user
    
    def _user_has_permission(self, user: User, resource: str, action: str) -> bool:
        """Check user permissions (implement based on your permission system)."""
        # Superusers have all permissions
        if user.is_superuser:
            return True
        
        # Basic permission logic - extend as needed
        user_permissions = {
            "persona": ["create", "read", "update"],
        }
        
        return action in user_permissions.get(resource, [])