"""API dependencies for authentication and authorization."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.db.session import get_session
from app.models.user import User
from app.services.jwt_service import decode_token

# HTTP Bearer security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Extracts the Bearer token from the Authorization header,
    decodes it, and loads the user from the database.
    
    Args:
        credentials: HTTP Authorization credentials containing the Bearer token
        
    Returns:
        The authenticated User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    token = credentials.credentials
    
    # Decode token to get user_id
    user_id = decode_token(token)
    if user_id is None:
        raise credentials_exception
    
    # Load user from database
    with get_session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        
        if user is None:
            raise credentials_exception
        
        # Detach user from session to use outside context
        session.expunge(user)
        
        return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure the current user is active.
    
    Can be extended to check for disabled/banned users.
    
    Args:
        current_user: The authenticated user from get_current_user
        
    Returns:
        The active User object
    """
    # Future: Add check for user.is_active if needed
    return current_user


async def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure the current user is an admin.
    
    Args:
        current_user: The authenticated user from get_current_user
        
    Returns:
        The admin User object
        
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_role(required_role: str):
    """
    Dependency factory to enforce role-based access control (RBAC).
    
    Creates a dependency that checks if the authenticated user has
    the specified role. Use this to protect endpoints by role.
    
    Usage:
        @router.get("/admin/users")
        def list_users(user=Depends(require_role("admin"))):
            ...
    
    Args:
        required_role: The role required to access the endpoint (e.g., "admin", "user")
        
    Returns:
        A dependency function that validates the user's role
        
    Raises:
        HTTPException 403: If user does not have the required role
    """
    async def role_dependency(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}"
            )
        return current_user
    return role_dependency
