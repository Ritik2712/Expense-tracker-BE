from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from Schemas.User import User
from exceptions import AdminAccessDenied, InvalidToken, NoRoleError, TokenNotProvide, UserNotFoundError
from utils.db import get_connection

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 100

def create_access_token(data: dict):
    if "role" not in data or not data["role"]:
        raise NoRoleError()
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials  # actual JWT string
    if not token:
        raise TokenNotProvide()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise InvalidToken()
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, role
                    FROM users
                    WHERE id = %s
                    """,
                    (user_id,)
                )

                row = cur.fetchone()
                if not row:
                    raise UserNotFoundError(user_id)
                return User(name=row[1],role=row[2],id=row[0])

    except JWTError:
        raise InvalidToken()

def require_role(required_role: str):
    def role_checker(current_user=Depends(get_current_user)):
        if current_user.role != required_role:
            raise AdminAccessDenied()
        return current_user
    return role_checker
