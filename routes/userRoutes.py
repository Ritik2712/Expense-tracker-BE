from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from uuid import UUID

from Service.OrchestratorService import OrchestratorService
from Service.UserService import UserService
from Schemas.User import User
from utils.auth import get_current_user
from utils.logging_config import get_logger


class UserRequest(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)


class UpdateUserRequest(BaseModel):
    name: str = Field(min_length=3, max_length=50)


logger = get_logger(__name__)


def create_user_router(user_service: UserService, orchestrator_service: OrchestratorService) -> APIRouter:
    user_router = APIRouter(prefix="/users")

    @user_router.get("/me")
    def fetch_user(current_user: User = Depends(get_current_user)):
        logger.info("action=users.fetch_me status=success")
        return {
            "user": {
                "id": current_user.id,
                "name": current_user.name,
                "role": current_user.role,
            }
        }

    @user_router.put("/update/{id}")
    def update_user(
        id: UUID,
        req: UpdateUserRequest,
        current_user: User = Depends(get_current_user),
    ):
        if str(id) != current_user.id:
            raise HTTPException(
                status_code=403,
                detail={"message": "You can't update this user"},
            )
        updated_user = user_service.update_user(str(id), req.name)
        logger.info("action=users.update status=success")
        return updated_user

    @user_router.delete("/{id}", status_code=204)
    def delete_user(
        id: UUID,
        current_user: User = Depends(get_current_user),
    ):
        if str(id) != current_user.id:
            raise HTTPException(
                status_code=403,
                detail={"message": "You can't delete this user"},
            )
        user_service.delete_user(str(id))
        logger.info("action=users.delete status=success")

    return user_router
