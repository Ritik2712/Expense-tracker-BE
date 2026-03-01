from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from time import perf_counter

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
from utils.logging_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)
app = FastAPI()

user_service = UserService()
account_service = AccountService()
auth_service = AuthService()
transaction_service = TransactionService(account_service)
orchestrator_service = OrchestratorService(user_service,account_service,transaction_service)


def _error_payload(message: str) -> dict:
    return {"detail": {"message": message}}


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _log_exception(request: Request, status_code: int, message: str) -> None:
    if status_code in (401, 403):
        logger.warning(
            "error status=%s path=%s ip=%s message=%s",
            status_code,
            request.url.path,
            _client_ip(request),
            message,
        )
        return
    logger.error(
        "error status=%s path=%s message=%s",
        status_code,
        request.url.path,
        message,
    )


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = perf_counter()
    response = await call_next(request)
    elapsed_ms = (perf_counter() - start) * 1000
    logger.info(
        "request method=%s path=%s status=%s duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


@app.exception_handler(InvalidUserType)
async def handle_invalid_user_type(request: Request, exc: InvalidUserType):
    _log_exception(request, 400, str(exc))
    return JSONResponse(status_code=400, content=_error_payload(str(exc)))


@app.exception_handler(UserAlreadyExistsError)
async def handle_user_exists(request: Request, exc: UserAlreadyExistsError):
    _log_exception(request, 400, str(exc))
    return JSONResponse(status_code=400, content=_error_payload(str(exc)))


@app.exception_handler(UserNotFoundError)
async def handle_user_not_found(request: Request, exc: UserNotFoundError):
    _log_exception(request, 404, str(exc))
    return JSONResponse(status_code=404, content=_error_payload(str(exc)))


@app.exception_handler(AccountNotFoundError)
async def handle_account_not_found(request: Request, exc: AccountNotFoundError):
    _log_exception(request, 404, str(exc))
    return JSONResponse(status_code=404, content=_error_payload(str(exc)))


@app.exception_handler(AccountAccessDeniedError)
async def handle_account_access_denied(request: Request, exc: AccountAccessDeniedError):
    _log_exception(request, 403, str(exc))
    return JSONResponse(status_code=403, content=_error_payload(str(exc)))


@app.exception_handler(InvalidTransactionTypeError)
async def handle_invalid_transaction_type(request: Request, exc: InvalidTransactionTypeError):
    _log_exception(request, 400, str(exc))
    return JSONResponse(status_code=400, content=_error_payload(str(exc)))


@app.exception_handler(InvalidCredentialsError)
async def handle_invalid_credentials(request: Request, exc: InvalidCredentialsError):
    _log_exception(request, 401, str(exc))
    return JSONResponse(status_code=401, content=_error_payload(str(exc)))


@app.exception_handler(InvalidTransaction)
async def handle_invalid_transaction(request: Request, exc: InvalidTransaction):
    _log_exception(request, 400, str(exc))
    return JSONResponse(status_code=400, content=_error_payload(str(exc)))


@app.exception_handler(TransactionAccountMismatchError)
async def handle_transaction_account_mismatch(request: Request, exc: TransactionAccountMismatchError):
    _log_exception(request, 400, str(exc))
    return JSONResponse(status_code=400, content=_error_payload(str(exc)))


@app.exception_handler(InvalidAccountError)
async def handle_invalid_account(request: Request, exc: InvalidAccountError):
    _log_exception(request, 400, str(exc))
    return JSONResponse(status_code=400, content=_error_payload(str(exc)))


@app.exception_handler(TransactionNotFoundError)
async def handle_transaction_not_found(request: Request, exc: TransactionNotFoundError):
    _log_exception(request, 404, str(exc))
    return JSONResponse(status_code=404, content=_error_payload(str(exc)))

@app.exception_handler(AdminAccessDenied)
async def handle_admin_access_denied(request: Request,exec: AdminAccessDenied):
    _log_exception(request, 403, str(exec))
    return JSONResponse(status_code=403, content=_error_payload(str(exec)))

@app.exception_handler(InvalidToken)
async def handle_invalid_token(request: Request,exec: InvalidToken):
    _log_exception(request, 401, str(exec))
    return JSONResponse(status_code=401, content=_error_payload(str(exec)))

@app.exception_handler(TokenNotProvide)
async def handle_no_token(request: Request,exec: TokenNotProvide):
    _log_exception(request, 401, str(exec))
    return JSONResponse(status_code=401, content=_error_payload(str(exec)))

@app.exception_handler(NoRoleError)
async def handle_no_role(request: Request,exec: NoRoleError):
    _log_exception(request, 401, str(exec))
    return JSONResponse(status_code=401, content=_error_payload(str(exec)))


@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exc: HTTPException):
    message = str(exc.detail)
    _log_exception(request, exc.status_code, message)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception):
    logger.exception("unexpected_error path=%s", request.url.path)
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
 
