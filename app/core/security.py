from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import List
from app.core.auth import decode_access_token
from app.models.user import TokenData, UserRole
from app.core.logger import get_logger

logger = get_logger()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    Decode JWT token and return the current user data.

    Raises HTTP 401 if token is invalid or expired.
    """
    user = decode_access_token(token)
    if not user:
        logger.warning("Invalid or expired token during authentication")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return user


def require_roles(required_roles: List[UserRole]):
    """
    Dependency to enforce role-based access control.

    Raises HTTP 403 if current user's role is not in required_roles.
    """
    def role_checker(current_user: TokenData = Depends(get_current_user)):
        if current_user.role not in required_roles:
            logger.warning(f"User role '{current_user.role}' lacks required permissions: {required_roles}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker
