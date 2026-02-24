from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from Service.AuthService import AuthService
from exceptions import InvalidCredentialsError, InvalidUserType, UserAlreadyExistsError
from utils.auth import create_access_token

class LoginRequest(BaseModel):
    name:str
    password:str

class RegisterRequest(BaseModel):
    name:str
    password:str

class AdminRegisterRequest(BaseModel):
    name: str
    password: str




def create_auth_router(auth_service: AuthService)->APIRouter:
    auth_router = APIRouter(prefix="/auth",tags=["Auth"])

    @auth_router.post("", status_code=201)
    def register_user(req: RegisterRequest):
        try:
            user = auth_service.register_user(req.name, req.password, "user")
            token = create_access_token({"sub":user.id,"name":user.name,"role":user.role})
            return {"message": "user created successfully", "user": {"name":user.name,"sub":user.id,"role":user.role, "token":token} }
        except UserAlreadyExistsError as e:
            raise HTTPException(status_code=400, detail={"message":str(e)})
        except InvalidUserType as e:
            raise HTTPException(status_code=400, detail={"message":str(e)})
            
    @auth_router.post("/admin", status_code=201)
    def register_admin(req: AdminRegisterRequest):
        try:
            user = auth_service.register_user(req.name, req.password, "admin")
            token = create_access_token({"sub":user.id,"name":user.name,"role":user.role})
            return {
                "message": "admin created successfully",
                "user": {
                    "name": user.name,
                    "id": user.id,
                    "role": user.role,
                    "token": token,
                },
            }
        except UserAlreadyExistsError as e:
            raise HTTPException(status_code=400, detail={"message": str(e)})
        except InvalidUserType as e:
            raise HTTPException(status_code=400, detail={"message": str(e)})


    
    @auth_router.post("/login")
    def login_user(req:LoginRequest):
        try:
            user = auth_service.login_user(req.name,req.password)
            token = create_access_token({"sub":user.id,"name":user.name,"role":user.role})
            return {"message":"login successful", "user":{"name":user.name,"id":user.id,"role":user.role,"token":token}}
        except InvalidCredentialsError as e:
            raise HTTPException(status_code=401, detail={"message": str(e)})
        except InvalidUserType as e:
            raise HTTPException(status_code=400, detail={"message":str(e)})
        


    return auth_router
