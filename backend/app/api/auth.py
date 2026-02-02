"""Authentication API endpoints for user registration and login."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
import uuid

from app.db.session import get_session
from app.models.user import User
from app.services.security import hash_password, verify_password
from app.services.jwt_service import create_access_token

router = APIRouter(prefix="/auth", tags=["authentication"])


class RegisterRequest(BaseModel):
    """Request model for user registration."""
    email: EmailStr
    password: str


class RegisterResponse(BaseModel):
    """Response model for user registration."""
    user_id: str
    email: str
    message: str


class LoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Response model for user login."""
    access_token: str
    token_type: str = "bearer"
    user_id: str


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest) -> RegisterResponse:
    """
    Register a new user.
    
    Args:
        request: RegisterRequest containing email and password
        
    Returns:
        RegisterResponse with user details
        
    Raises:
        HTTPException: If email already exists
    """
    with get_session() as session:
        # Check if email already exists
        existing_user = session.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user_id = str(uuid.uuid4())
        hashed_pwd = hash_password(request.password)
        
        new_user = User(
            user_id=user_id,
            email=request.email,
            hashed_password=hashed_pwd,
            role="user"
        )
        
        session.add(new_user)
        session.commit()
        
        return RegisterResponse(
            user_id=user_id,
            email=request.email,
            message="User registered successfully"
        )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    """
    Authenticate user and return JWT token.
    
    Args:
        request: LoginRequest containing email and password
        
    Returns:
        LoginResponse with JWT access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    with get_session() as session:
        # Find user by email
        user = session.query(User).filter(User.email == request.email).first()
        
        if not user or not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Verify password
        if not verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.user_id, "email": user.email, "role": user.role}
        )
        
        return LoginResponse(
            access_token=access_token,
            user_id=user.user_id
        )
