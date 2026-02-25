from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from Service.TransactionService import TransactionService
from Schemas.User import User
from exceptions import (
    InvalidTransaction,
    TransactionNotFoundError,
    TransactionAccountMismatchError,
    AccountNotFoundError,
    AccountAccessDeniedError,
    InvalidTransactionTypeError,
    UserNotFoundError,
)
from utils.auth import get_current_user


class CreateTransactionRequest(BaseModel):
    amount: float
    transaction_type: str
    description: str
    account_id: UUID


class UpdateTransactionRequest(BaseModel):
    amount: float
    transaction_type: str
    description: str
    account_id: UUID


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
        try:
            new_transaction = transaction_service.create_transaction(
                amount=req.amount,
                transaction_type=req.transaction_type,
                description=req.description,
                account_id=str(req.account_id),
                user_id=str(user_id),
            )
            return {"message": "transaction created successfully", "Transaction":new_transaction}

        except AccountNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})
        except AccountAccessDeniedError as e:
            raise HTTPException(status_code=403, detail={"message": str(e)})
        except InvalidTransactionTypeError as e:
            raise HTTPException(status_code=400, detail={"message": str(e)})
        except UserNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})
        except InvalidTransaction as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})

    @transaction_router.get("/{transaction_id}")
    def get_transaction(
        transaction_id: UUID,
        user_id: UUID,
        account_id: UUID,
        current_user: User = Depends(get_current_user),
    ):
        try:
            tx = transaction_service.get_transaction_by_id(str(transaction_id), str(user_id),str(account_id))
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

    @transaction_router.get("")
    def get_transactions(
        account_id: UUID,
        user_id: UUID,
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        current_user: User = Depends(get_current_user),
    ):
        try:
            transactions = transaction_service.get_transactions_by_account(
                str(account_id), str(user_id), page=page, limit=limit
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

        except AccountNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})
        except AccountAccessDeniedError as e:
            raise HTTPException(status_code=403, detail={"message": str(e)})
        except UserNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})

    @transaction_router.get("/user/all")
    def get_transactions_for_user(
        user_id: UUID,
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        current_user: User = Depends(get_current_user),
    ):
        try:
            transactions = transaction_service.get_transactions_by_user(
                str(user_id), page=page, limit=limit
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
        except UserNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})

    @transaction_router.put("/{transaction_id}")
    def update_transaction(
        transaction_id: UUID,
        user_id: UUID,
        req: UpdateTransactionRequest,
        current_user: User = Depends(get_current_user),
    ):
        try:
            transaction_service.edit_transaction(
                transaction_id=str(transaction_id),
                amount=req.amount,
                transaction_type=req.transaction_type,
                description=req.description,
                account_id=str(req.account_id),
                user_id=str(user_id),
            )
            return {"message": "transaction updated successfully"}

        except TransactionNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})
        except AccountNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})
        except AccountAccessDeniedError as e:
            raise HTTPException(status_code=403, detail={"message": str(e)})
        except InvalidTransactionTypeError as e:
            raise HTTPException(status_code=400, detail={"message": str(e)})
        except UserNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})

    @transaction_router.delete("/{transaction_id}", status_code=204)
    def delete_transaction(
        transaction_id: UUID,
        user_id: UUID,
        current_user: User = Depends(get_current_user),
    ):
        try:
            transaction_service.deleteTransaction(
                user_id=str(user_id),
                transaction_id=str(transaction_id),
            )

        except TransactionNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})
        except TransactionAccountMismatchError as e:
            raise HTTPException(status_code=400, detail={"message": str(e)})
        except AccountNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})
        except AccountAccessDeniedError as e:
            raise HTTPException(status_code=403, detail={"message": str(e)})
        except UserNotFoundError as e:
            raise HTTPException(status_code=404, detail={"message": str(e)})

    return transaction_router
