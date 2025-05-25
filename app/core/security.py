from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.auth import decode_access_token
from app.models.user import TokenData, RoleEnum

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# Get current user from token
def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    user = decode_access_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user

# Role-based access
def require_role(required_roles: list[RoleEnum]):
    def role_checker(current_user: TokenData = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user
    return role_checker
