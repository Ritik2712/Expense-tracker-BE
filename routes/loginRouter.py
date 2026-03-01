from fastapi import APIRouter
from pydantic import BaseModel, Field

from Service.AuthService import AuthService
from utils.auth import create_access_token
from utils.logging_config import get_logger


class LoginRequest(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)


class RegisterRequest(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)


class AdminRegisterRequest(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)


logger = get_logger(__name__)


def create_auth_router(auth_service: AuthService) -> APIRouter:
    auth_router = APIRouter(prefix="/auth", tags=["Auth"])

    @auth_router.post("", status_code=201)
    def register_user(req: RegisterRequest):
        user = auth_service.register_user(req.name, req.password, "user")
        token = create_access_token({"sub": user.id, "name": user.name, "role": user.role})
        logger.info("action=auth.register_user status=success")
        return {
            "message": "user created successfully",
            "user": {"name": user.name, "sub": user.id, "role": user.role, "token": token},
        }

    @auth_router.post("/admin", status_code=201)
    def register_admin(req: AdminRegisterRequest):
        user = auth_service.register_user(req.name, req.password, "admin")
        token = create_access_token({"sub": user.id, "name": user.name, "role": user.role})
        logger.info("action=auth.register_admin status=success")
        return {
            "message": "admin created successfully",
            "user": {
                "name": user.name,
                "id": user.id,
                "role": user.role,
                "token": token,
            },
        }

    @auth_router.post("/login")
    def login_user(req: LoginRequest):
        user = auth_service.login_user(req.name, req.password)
        token = create_access_token({"sub": user.id, "name": user.name, "role": user.role})
        logger.info("action=auth.login status=success")
        return {
            "message": "login successful",
            "user": {"name": user.name, "id": user.id, "role": user.role, "token": token},
        }

    return auth_router
