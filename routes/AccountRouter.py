from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from Service.AccountService import AccountService
from Service.OrchestratorService import OrchestratorService
from Schemas.User import User
from exceptions import (
    AccountNotFoundError,
    AccountAccessDeniedError,
    InvalidAccountError,
    UserNotFoundError,
)
from utils.auth import get_current_user


class CreateAccountRequest(BaseModel):
    name: str


class UpdateAccountRequest(BaseModel):
    name: str
    balance: float


def create_account_router(account_service: AccountService, orchestrator_service: OrchestratorService) -> APIRouter:
    account_router = APIRouter(prefix="/accounts")

    @account_router.post("", status_code=201)
    def create_account(
        req: CreateAccountRequest,
        user: User = Depends(get_current_user),
    ):
        try:
            account = account_service.create_account(user.id, req.name)
            return {
                "message": "account created successfully",
                "account": {
                    "id": account.id,
                    "name": account.name,
                    "balance": account.balance,
                },
            }
        except UserNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})
        except InvalidAccountError as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})

    @account_router.get("")
    def get_accounts(
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        user: User = Depends(get_current_user),
    ):
        try:
            accounts = account_service.get_all_accounts_of_user(
                user_id=user.id,
                page=page,
                limit=limit,
            )
            return [
                {
                    "id": acc.id,
                    "name": acc.name,
                    "balance": acc.balance,
                }
                for acc in accounts
            ]
        except UserNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})

    @account_router.put("/{account_id}")
    def update_account(
        account_id: UUID,
        req: UpdateAccountRequest,
        user: User = Depends(get_current_user),
    ):
        try:
            account_service.update_account(
                user_id=user.id,
                balance=req.balance,
                account_id=account_id,
                account_name=req.name,
            )
            return {"message": "account updated successfully"}
        except AccountNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})
        except AccountAccessDeniedError as e:
            raise HTTPException(status_code=403, detail={"message": str(e)})

    @account_router.delete("/{account_id}", status_code=204)
    def delete_account(
        account_id: UUID,
        user: User = Depends(get_current_user),
    ):
        try:
            account_service.deleteAccount(user.id, account_id)
        except AccountNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})
        except AccountAccessDeniedError as e:
            raise HTTPException(status_code=403, detail={"message": str(e)})
        except UserNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})

    return account_router
