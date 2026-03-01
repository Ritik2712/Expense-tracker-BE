from uuid import UUID
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from Service.TransactionService import TransactionService
from Schemas.User import User
from utils.auth import get_current_user
from utils.logging_config import get_logger


class CreateTransactionRequest(BaseModel):
    amount: float = Field(ge=0)
    transaction_type: str = Field(min_length=3, max_length=20)
    description: str = Field(min_length=1, max_length=300)
    account_id: UUID


class UpdateTransactionRequest(BaseModel):
    amount: float = Field(ge=0)
    transaction_type: str = Field(min_length=3, max_length=20)
    description: str = Field(min_length=1, max_length=300)
    account_id: UUID


logger = get_logger(__name__)


def create_transaction_router(
    transaction_service: TransactionService,
) -> APIRouter:

    transaction_router = APIRouter(prefix="/transactions")

    @transaction_router.post("", status_code=201)
    def create_transaction(
        user_id: UUID,
        req: CreateTransactionRequest,
        current_user: User = Depends(get_current_user),
    ):
        new_transaction = transaction_service.create_transaction(
            amount=req.amount,
            transaction_type=req.transaction_type,
            description=req.description,
            account_id=str(req.account_id),
            user_id=str(user_id),
        )
        logger.info("action=transactions.create status=success")
        return {"message": "transaction created successfully", "Transaction": new_transaction}

    @transaction_router.get("/{transaction_id}")
    def get_transaction(
        transaction_id: UUID,
        user_id: UUID,
        account_id: UUID,
        current_user: User = Depends(get_current_user),
    ):
        tx = transaction_service.get_transaction_by_id(str(transaction_id), str(user_id), str(account_id))
        logger.info("action=transactions.get_one status=success")
        return {
            "transaction": {
                "id": tx.id,
                "amount": tx.amount,
                "transaction_type": tx.transaction_type,
                "description": tx.description,
                "account_id": tx.account_id,
            }
        }

    @transaction_router.get("")
    def get_transactions(
        account_id: UUID,
        user_id: UUID,
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        current_user: User = Depends(get_current_user),
    ):
        transactions = transaction_service.get_transactions_by_account(
            str(account_id), str(user_id), page=page, limit=limit
        )
        logger.info("action=transactions.list_by_account status=success")
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

    @transaction_router.get("/user/all")
    def get_transactions_for_user(
        user_id: UUID,
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        current_user: User = Depends(get_current_user),
    ):
        transactions = transaction_service.get_transactions_by_user(
            str(user_id), page=page, limit=limit
        )
        logger.info("action=transactions.list_by_user status=success")
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

    @transaction_router.put("/{transaction_id}")
    def update_transaction(
        transaction_id: UUID,
        user_id: UUID,
        req: UpdateTransactionRequest,
        current_user: User = Depends(get_current_user),
    ):
        transaction_service.edit_transaction(
            transaction_id=str(transaction_id),
            amount=req.amount,
            transaction_type=req.transaction_type,
            description=req.description,
            account_id=str(req.account_id),
            user_id=str(user_id),
        )
        logger.info("action=transactions.update status=success")
        return {"message": "transaction updated successfully"}

    @transaction_router.delete("/{transaction_id}", status_code=204)
    def delete_transaction(
        transaction_id: UUID,
        user_id: UUID,
        current_user: User = Depends(get_current_user),
    ):
        transaction_service.deleteTransaction(
            user_id=str(user_id),
            transaction_id=str(transaction_id),
        )
        logger.info("action=transactions.delete status=success")

    return transaction_router
