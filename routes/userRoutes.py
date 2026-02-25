from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from uuid import UUID


from Service.OrchestratorService import OrchestratorService
from Service.UserService import UserService
from Schemas.User import User
from utils.auth import get_current_user

class UserRequest(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)

class UpdateUserRequest(BaseModel):
    name: str = Field(min_length=3, max_length=50)



def create_user_router(user_service: UserService,orchestrator_service: OrchestratorService)->APIRouter:
    user_router = APIRouter(prefix="/users")

    @user_router.get("/me")
    def fetchUser(
        current_user: User = Depends(get_current_user),
    ):
        return {"user": {"id": current_user.id, "name": current_user.name, "role": current_user.role}}
    
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
        updated_user = user_service.update_user(str(id),req.name)
        return updated_user
    
    @user_router.delete("/{id}",status_code=204)
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
    
    return user_router
