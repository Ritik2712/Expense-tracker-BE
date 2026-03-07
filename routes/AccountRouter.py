from uuid import UUID
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from Service.AccountService import AccountService
from Service.OrchestratorService import OrchestratorService
from Schemas.User import User
from utils.auth import get_current_user
from utils.logging_config import get_logger


class CreateAccountRequest(BaseModel):
    name: str = Field(min_length=3, max_length=50)


class UpdateAccountRequest(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    balance: float = Field(ge=0)


logger = get_logger(__name__)


def create_account_router(account_service: AccountService, orchestrator_service: OrchestratorService) -> APIRouter:
    account_router = APIRouter(prefix="/accounts")

    @account_router.post("", status_code=201)
    def create_account(
        req: CreateAccountRequest,
        user: User = Depends(get_current_user),
    ):
        account = account_service.create_account(str(user.id), req.name)
        logger.info("action=accounts.create status=success")
        return {
            "message": "account created successfully",
            "account": {
                "id": account.id,
                "name": account.name,
                "balance": account.balance,
            },
        }

    @account_router.get("")
    def get_accounts(
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        user: User = Depends(get_current_user),
    ):
        accounts = account_service.get_all_accounts_of_user(
            user_id=str(user.id),
            page=page,
            limit=limit,
        )
        logger.info("action=accounts.list status=success")
        return [
            {
                "id": acc.id,
                "name": acc.name,
                "balance": acc.balance,
            }
            for acc in accounts
        ]

    @account_router.put("/{account_id}")
    def update_account(
        account_id: UUID,
        req: UpdateAccountRequest,
        user: User = Depends(get_current_user),
    ):
        account_service.update_account(
            user_id=str(user.id),
            balance=req.balance,
            account_id=str(account_id),
            account_name=req.name,
        )
        logger.info("action=accounts.update status=success")
        return {"message": "account updated successfully"}

    @account_router.delete("/{account_id}", status_code=204)
    def delete_account(
        account_id: UUID,
        user: User = Depends(get_current_user),
    ):
        account_service.deleteAccount(str(user.id), str(account_id))
        logger.info("action=accounts.delete status=success")

    return account_router
