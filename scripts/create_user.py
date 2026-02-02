"""Script to create a user (including admin) in the Financial Planner application."""

import sys
import os
import uuid
import argparse

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.db.session import get_session
from app.models.user import User
from app.services.security import hash_password


def create_user(email: str, password: str, role: str = "user") -> None:
    """
    Create a new user in the database.
    
    Args:
        email: User's email address
        password: Plain text password (will be hashed)
        role: User role - either "user" or "admin"
    """
    if role not in ["user", "admin"]:
        print(f"Error: Invalid role '{role}'. Must be 'user' or 'admin'.")
        sys.exit(1)
    
    with get_session() as session:
        # Check if email already exists
        existing_user = session.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"Error: User with email '{email}' already exists.")
            sys.exit(1)
        
        # Create user
        user_id = str(uuid.uuid4())
        hashed_pwd = hash_password(password)
        
        new_user = User(
            user_id=user_id,
            email=email,
            hashed_password=hashed_pwd,
            role=role
        )
        
        session.add(new_user)
        session.commit()
        
        print(f"✅ User created successfully!")
        print(f"   Email: {email}")
        print(f"   User ID: {user_id}")
        print(f"   Role: {role}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a user in the Financial Planner database")
    parser.add_argument("--email", "-e", required=True, help="User's email address")
    parser.add_argument("--password", "-p", required=True, help="User's password")
    parser.add_argument("--role", "-r", default="user", choices=["user", "admin"], 
                        help="User role (default: user)")
    
    args = parser.parse_args()
    
    create_user(args.email, args.password, args.role)
