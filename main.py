from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from Service.AuthService import AuthService
from Service.UserService import UserService
from Service.AccountService import AccountService
from Service.TransactionService import TransactionService
from Service.OrchestratorService import OrchestratorService
from exceptions import (
    AccountAccessDeniedError,
    AccountNotFoundError,
    AdminAccessDenied,
    InvalidAccountError,
    InvalidCredentialsError,
    InvalidToken,
    InvalidTransaction,
    InvalidTransactionTypeError,
    InvalidUserType,
    NoRoleError,
    TokenNotProvide,
    TransactionAccountMismatchError,
    TransactionNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
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


def _error_payload(message: str) -> dict:
    return {"detail": {"message": message}}


@app.exception_handler(InvalidUserType)
async def handle_invalid_user_type(request: Request, exc: InvalidUserType):
    return JSONResponse(status_code=400, content=_error_payload(str(exc)))


@app.exception_handler(UserAlreadyExistsError)
async def handle_user_exists(request: Request, exc: UserAlreadyExistsError):
    return JSONResponse(status_code=400, content=_error_payload(str(exc)))


@app.exception_handler(UserNotFoundError)
async def handle_user_not_found(request: Request, exc: UserNotFoundError):
    return JSONResponse(status_code=404, content=_error_payload(str(exc)))


@app.exception_handler(AccountNotFoundError)
async def handle_account_not_found(request: Request, exc: AccountNotFoundError):
    return JSONResponse(status_code=404, content=_error_payload(str(exc)))


@app.exception_handler(AccountAccessDeniedError)
async def handle_account_access_denied(request: Request, exc: AccountAccessDeniedError):
    return JSONResponse(status_code=403, content=_error_payload(str(exc)))


@app.exception_handler(InvalidTransactionTypeError)
async def handle_invalid_transaction_type(request: Request, exc: InvalidTransactionTypeError):
    return JSONResponse(status_code=400, content=_error_payload(str(exc)))


@app.exception_handler(InvalidCredentialsError)
async def handle_invalid_credentials(request: Request, exc: InvalidCredentialsError):
    return JSONResponse(status_code=401, content=_error_payload(str(exc)))


@app.exception_handler(InvalidTransaction)
async def handle_invalid_transaction(request: Request, exc: InvalidTransaction):
    return JSONResponse(status_code=400, content=_error_payload(str(exc)))


@app.exception_handler(TransactionAccountMismatchError)
async def handle_transaction_account_mismatch(request: Request, exc: TransactionAccountMismatchError):
    return JSONResponse(status_code=400, content=_error_payload(str(exc)))


@app.exception_handler(InvalidAccountError)
async def handle_invalid_account(request: Request, exc: InvalidAccountError):
    return JSONResponse(status_code=400, content=_error_payload(str(exc)))


@app.exception_handler(TransactionNotFoundError)
async def handle_transaction_not_found(request: Request, exc: TransactionNotFoundError):
    return JSONResponse(status_code=404, content=_error_payload(str(exc)))

@app.exception_handler(AdminAccessDenied)
async def handle_admin_access_denied(request: Request,exec: AdminAccessDenied):
    return JSONResponse(status_code=403, content=_error_payload(str(exec)))

@app.exception_handler(InvalidToken)
async def handle_invalid_token(request: Request,exec: InvalidToken):
    return JSONResponse(status_code=401, content=_error_payload(str(exec)))

@app.exception_handler(TokenNotProvide)
async def handle_no_token(request: Request,exec: TokenNotProvide):
    return JSONResponse(status_code=401, content=_error_payload(str(exec)))

@app.exception_handler(NoRoleError)
async def handle_no_role(request: Request,exec: NoRoleError):
    return JSONResponse(status_code=401, content=_error_payload(str(exec)))

@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception):
    # optional: log `exc` internally here
    return JSONResponse(
        status_code=500,
        content=_error_payload("Internal server error"),
    )

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
 
