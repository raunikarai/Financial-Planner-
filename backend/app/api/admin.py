"""Admin API endpoints - restricted to admin role only."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.dependencies import require_role
from app.db.session import get_session
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


# ==================== Response Models ====================

class UserResponse(BaseModel):
    """Response model for user data (excludes password)."""
    id: int
    user_id: str
    email: str
    role: str
    
    class Config:
        from_attributes = True


class SystemHealthResponse(BaseModel):
    """Response model for system health check."""
    status: str
    database: str
    user_count: int
    expense_count: int


# ==================== Admin Endpoints ====================

@router.get("/users", response_model=List[UserResponse])
async def list_all_users(
    admin_user: User = Depends(require_role("admin"))
) -> List[UserResponse]:
    """
    List all users in the system.
    
    Admin-only endpoint.
    
    Returns:
        List of all users (without password hashes)
    """
    with get_session() as session:
        users = session.query(User).all()
        return [
            UserResponse(
                id=u.id,
                user_id=u.user_id,
                email=u.email or "",
                role=u.role or "user"
            )
            for u in users
        ]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    admin_user: User = Depends(require_role("admin"))
) -> UserResponse:
    """
    Get a specific user by user_id.
    
    Admin-only endpoint.
    
    Args:
        user_id: The user's unique identifier
        
    Returns:
        User data (without password hash)
        
    Raises:
        404 if user not found
    """
    with get_session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id '{user_id}' not found"
            )
        
        return UserResponse(
            id=user.id,
            user_id=user.user_id,
            email=user.email or "",
            role=user.role or "user"
        )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin_user: User = Depends(require_role("admin"))
) -> dict:
    """
    Delete a user by user_id.
    
    Admin-only endpoint. Cannot delete yourself.
    
    Args:
        user_id: The user's unique identifier
        
    Returns:
        Confirmation message
        
    Raises:
        404 if user not found
        400 if trying to delete yourself
    """
    if admin_user.user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    with get_session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id '{user_id}' not found"
            )
        
        session.delete(user)
        session.commit()
        
        return {"message": f"User '{user_id}' deleted successfully"}


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    new_role: str,
    admin_user: User = Depends(require_role("admin"))
) -> UserResponse:
    """
    Update a user's role.
    
    Admin-only endpoint.
    
    Args:
        user_id: The user's unique identifier
        new_role: The new role to assign ("user" or "admin")
        
    Returns:
        Updated user data
        
    Raises:
        404 if user not found
        400 if invalid role
    """
    valid_roles = ["user", "admin"]
    if new_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {valid_roles}"
        )
    
    with get_session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id '{user_id}' not found"
            )
        
        user.role = new_role
        session.commit()
        session.refresh(user)
        
        return UserResponse(
            id=user.id,
            user_id=user.user_id,
            email=user.email or "",
            role=user.role or "user"
        )


@router.get("/health", response_model=SystemHealthResponse)
async def system_health(
    admin_user: User = Depends(require_role("admin"))
) -> SystemHealthResponse:
    """
    Get system health and statistics.
    
    Admin-only endpoint.
    
    Returns:
        System health status and counts
    """
    from app.models.expense import Expense
    
    with get_session() as session:
        user_count = session.query(User).count()
        expense_count = session.query(Expense).count()
        
        return SystemHealthResponse(
            status="healthy",
            database="connected",
            user_count=user_count,
            expense_count=expense_count
        )
