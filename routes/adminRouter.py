from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from Service.AccountService import AccountService
from Service.TransactionService import TransactionService
from Service.UserService import UserService
from Schemas.User import User
from utils.auth import get_current_user, require_role
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
    def get_user(
        user_id: UUID,
        current_user: User = Depends(get_current_user),
    ):
        user = user_service.get_user(str(user_id))
        logger.info(
            "action=admin.users.get_one status=success admin_user_id=%s target_user_id=%s",
            current_user.id,
            user.id,
        )
        return {"user": {"id": user.id, "name": user.name, "role": user.role}}

    @admin_router.delete("/users/{user_id}", status_code=204)
    def delete_user(
        user_id: UUID,
        current_user: User = Depends(get_current_user),
    ):
        target_user = user_service.get_user(str(user_id))

        if target_user.id == current_user.id:
            raise HTTPException(
                status_code=403,
                detail={"message": "Admin cannot delete their own account."},
            )

        if target_user.role == "admin":
            admin_count = user_service.count_users_by_role("admin")
            if admin_count <= 1:
                raise HTTPException(
                    status_code=400,
                    detail={"message": "Cannot delete the last admin user."},
                )

        user_service.delete_user(str(user_id))
        logger.info(
            "action=admin.users.delete status=success admin_user_id=%s target_user_id=%s",
            current_user.id,
            target_user.id,
        )

    @admin_router.get("/users")
    def get_all_users(
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        current_user: User = Depends(get_current_user),
    ):
        allusers = user_service.get_all_users(page=page, limit=limit)
        logger.info(
            "action=admin.users.list status=success admin_user_id=%s page=%s limit=%s count=%s",
            current_user.id,
            page,
            limit,
            len(allusers),
        )
        return [
            {"id": user.id, "name": user.name, "role": user.role}
            for user in allusers
        ]

    @admin_router.get("/accounts/{account_id}")
    def get_account(
        account_id: UUID,
        current_user: User = Depends(get_current_user),
    ):
        account = account_service.get_account_admin(str(account_id))
        logger.info(
            "action=admin.accounts.get_one status=success admin_user_id=%s target_account_id=%s",
            current_user.id,
            account.id,
        )
        return {
            "account": {
                "id": account.id,
                "name": account.name,
                "user_id": account.user_id,
                "balance": account.balance,
            }
        }

    @admin_router.get("/accounts")
    def get_all_accounts(
        current_user: User = Depends(get_current_user),
    ):
        accounts = account_service.get_all_accounts_admin()
        logger.info(
            "action=admin.accounts.list status=success admin_user_id=%s count=%s",
            current_user.id,
            len(accounts),
        )
        return [
            {
                "id": account.id,
                "name": account.name,
                "user_id": account.user_id,
                "balance": account.balance,
            }
            for account in accounts
        ]

    @admin_router.delete("/accounts/{account_id}", status_code=204)
    def delete_account(
        account_id: UUID,
        current_user: User = Depends(get_current_user),
    ):
        account_service.delete_account_admin(str(account_id))
        logger.info(
            "action=admin.accounts.delete status=success admin_user_id=%s target_account_id=%s",
            current_user.id,
            str(account_id),
        )

    @admin_router.get("/transactions/{transaction_id}")
    def get_transaction(
        transaction_id: UUID,
        current_user: User = Depends(get_current_user),
    ):
        tx = transaction_service.get_transaction_admin(str(transaction_id))
        logger.info(
            "action=admin.transactions.get_one status=success admin_user_id=%s target_transaction_id=%s",
            current_user.id,
            tx.id,
        )
        return {
            "transaction": {
                "id": tx.id,
                "amount": tx.amount,
                "transaction_type": tx.transaction_type,
                "description": tx.description,
                "account_id": tx.account_id,
            }
        }

    @admin_router.get("/transactions")
    def get_all_transactions(
        current_user: User = Depends(get_current_user),
    ):
        transactions = transaction_service.get_all_transactions_admin()
        logger.info(
            "action=admin.transactions.list status=success admin_user_id=%s count=%s",
            current_user.id,
            len(transactions),
        )
        return [
            {
                "id": tx.id,
                "amount": tx.amount,
                "transaction_type": tx.transaction_type,
                "description": tx.description,
                "account_id": tx.account_id,
            }
            for tx in transactions
        ]

    @admin_router.delete("/transactions/{transaction_id}", status_code=204)
    def delete_transaction(
        transaction_id: UUID,
        current_user: User = Depends(get_current_user),
    ):
        transaction_service.delete_transaction_admin(str(transaction_id))
        logger.info(
            "action=admin.transactions.delete status=success admin_user_id=%s target_transaction_id=%s",
            current_user.id,
            str(transaction_id),
        )

    return admin_router
