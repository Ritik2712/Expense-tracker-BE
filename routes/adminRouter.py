from uuid import UUID

from fastapi import APIRouter, Depends, Query

from Service.AccountService import AccountService
from Service.TransactionService import TransactionService
from Service.UserService import UserService
from utils.auth import require_role
from utils.logging_config import get_logger


logger = get_logger(__name__)


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
        user = user_service.get_user(str(user_id))
        logger.info("action=admin.users.get_one status=success")
        return {"user": {"id": user.id, "name": user.name, "role": user.role}}

    @admin_router.delete("/users/{user_id}", status_code=204)
    def delete_user(user_id: UUID):
        user_service.delete_user(str(user_id))
        logger.info("action=admin.users.delete status=success")

    @admin_router.get("/users")
    def get_all_users(
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
    ):
        allusers = user_service.get_all_users(page=page, limit=limit)
        logger.info("action=admin.users.list status=success")
        return [
            {"id": user.id, "name": user.name, "role": user.role}
            for user in allusers
        ]

    @admin_router.get("/accounts/{account_id}")
    def get_account(account_id: UUID):
        account = account_service.get_account_admin(str(account_id))
        logger.info("action=admin.accounts.get_one status=success")
        return {
            "account": {
                "id": account.id,
                "name": account.name,
                "user_id": account.user_id,
                "balance": account.balance,
            }
        }

    @admin_router.delete("/accounts/{account_id}", status_code=204)
    def delete_account(account_id: UUID):
        account_service.delete_account_admin(str(account_id))
        logger.info("action=admin.accounts.delete status=success")

    @admin_router.get("/transactions/{transaction_id}")
    def get_transaction(transaction_id: UUID):
        tx = transaction_service.get_transaction_admin(str(transaction_id))
        logger.info("action=admin.transactions.get_one status=success")
        return {
            "transaction": {
                "id": tx.id,
                "amount": tx.amount,
                "transaction_type": tx.transaction_type,
                "description": tx.description,
                "account_id": tx.account_id,
            }
        }

    @admin_router.delete("/transactions/{transaction_id}", status_code=204)
    def delete_transaction(transaction_id: UUID):
        transaction_service.delete_transaction_admin(str(transaction_id))
        logger.info("action=admin.transactions.delete status=success")

    return admin_router
