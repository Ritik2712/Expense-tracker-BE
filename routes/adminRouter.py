from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from Service.AccountService import AccountService
from Service.TransactionService import TransactionService
from Service.UserService import UserService
from exceptions import AccountNotFoundError, TransactionNotFoundError, UserNotFoundError
from utils.auth import require_role


def create_admin_router(
    user_service: UserService,
    account_service: AccountService,
    transaction_service: TransactionService,
) -> APIRouter:
    admin_router = APIRouter(
        prefix="/admin",
        tags=["Admin"],
        dependencies=[Depends(require_role("admin"))],
    )

    @admin_router.get("/users/{user_id}")
    def get_user(user_id: UUID):
        try:
            user = user_service.get_user(str(user_id))
            return {"user": {"id": user.id, "name": user.name, "role": user.role}}
        except UserNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})

    @admin_router.delete("/users/{user_id}", status_code=204)
    def delete_user(user_id: UUID):
        try:
            user_service.delete_user(str(user_id))
        except UserNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})

    @admin_router.get("/users")
    def get_all_users(
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
    ):
        try:
            allusers = user_service.get_all_users(page=page, limit=limit)
            return [
                {"id": user.id, "name": user.name, "role": user.role}
                for user in allusers
            ]
        except UserNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})

    @admin_router.get("/accounts/{account_id}")
    def get_account(account_id: UUID):
        try:
            account = account_service.get_account_admin(str(account_id))
            return {
                "account": {
                    "id": account.id,
                    "name": account.name,
                    "user_id": account.user_id,
                    "balance": account.balance,
                }
            }
        except AccountNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})

    @admin_router.delete("/accounts/{account_id}", status_code=204)
    def delete_account(account_id: UUID):
        try:
            account_service.delete_account_admin(str(account_id))
        except AccountNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})

    @admin_router.get("/transactions/{transaction_id}")
    def get_transaction(transaction_id: UUID):
        try:
            tx = transaction_service.get_transaction_admin(str(transaction_id))
            return {
                "transaction": {
                    "id": tx.id,
                    "amount": tx.amount,
                    "transaction_type": tx.transaction_type,
                    "description": tx.description,
                    "account_id": tx.account_id,
                }
            }
        except TransactionNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})

    @admin_router.delete("/transactions/{transaction_id}", status_code=204)
    def delete_transaction(transaction_id: UUID):
        try:
            transaction_service.delete_transaction_admin(str(transaction_id))
        except TransactionNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})

    return admin_router
