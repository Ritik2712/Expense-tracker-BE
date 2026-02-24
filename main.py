from fastapi import FastAPI, HTTPException

from Service.AuthService import AuthService
from Service.UserService import UserService
from Service.AccountService import AccountService
from Service.TransactionService import TransactionService
from Service.OrchestratorService import OrchestratorService
from routes.AccountRouter import create_account_router
from routes.TransactionRouter import create_transaction_router
from routes.adminRouter import create_admin_router
from routes.loginRouter import create_auth_router
from routes.userRoutes import create_user_router

app = FastAPI()

user_service = UserService()
account_service = AccountService()
auth_service = AuthService()
transaction_service = TransactionService(account_service)
orchestrator_service = OrchestratorService(user_service,account_service,transaction_service)

@app.get("/health")
def health():
    return {"ok": True}

app.include_router(create_auth_router(auth_service))
app.include_router(create_user_router(user_service, orchestrator_service))
app.include_router(create_account_router(account_service, orchestrator_service))
app.include_router(create_transaction_router(transaction_service))
app.include_router(
    create_admin_router(user_service, account_service, transaction_service)
)
 
