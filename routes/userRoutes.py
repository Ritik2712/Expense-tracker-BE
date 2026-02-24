from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from uuid import UUID


from Service.OrchestratorService import OrchestratorService
from Service.UserService import UserService
from Schemas.User import User
from exceptions import AccountNotFoundError, InvalidCredentialsError, TransactionNotFoundError, UserAlreadyExistsError, UserNotFoundError
from utils.auth import get_current_user

class UserRequest(BaseModel):
    name:str
    password:str

class UpdateUserRequest(BaseModel):
    name:str



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
        try:
            if str(id) != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail={"message": "You can't update this user"},
                )
            updated_user = user_service.update_user(str(id),req.name)
            return updated_user
        except UserNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message":str(e)}) 
        except UserAlreadyExistsError as e:
            raise HTTPException(status_code=400, detail={"message":str(e)})
    
    @user_router.delete("/{id}",status_code=204)
    def delete_user(
        id: UUID,
        current_user: User = Depends(get_current_user),
    ):
        try:
            if str(id) != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail={"message": "You can't delete this user"},
                )
            user_service.delete_user(str(id))
        except UserNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message":str(e)}) 
        except AccountNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message":str(e)}) 
        except TransactionNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message":str(e)}) 
    
    return user_router
