from uuid import UUID
from Schemas.Transaction import Transaction
from Service.AccountService import AccountService
from exceptions import (
    TransactionNotFoundError,
    TransactionAccountMismatchError,
)
from utils.db import get_connection


class TransactionService:
    def __init__(self, account_service: AccountService):
        self._account_service = account_service

    def create_transaction(
        self,
        amount: float,
        transaction_type: str,
        description: str,
        account_id: str,
        user_id: str,
    ) -> Transaction:
        self._account_service.get_user_account(account_id, user_id)

        with get_connection() as conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    INSERT INTO transactions (account_id,description,amount, transaction_type)
                    VALUES (%s,%s,%s,%s)
                    RETURNING id, account_id,description,amount,transaction_type
                    """,
                    (account_id,description,amount,transaction_type)
                )
                row = cur.fetchone()
                transaction = Transaction(
                    id=row[0],
                    account_id=row[1],
                    description=row[2],
                    amount=float(row[3]),
                    transaction_type=row[4],
                )

                new_balance = self._account_service.update_account_balance(
                    amount, account_id, transaction_type,user_id,cur
                )
                return transaction

    def get_transaction_by_id(self, transaction_id: str, user_id:str, account_id:str) -> Transaction:
        self._account_service.get_user_account(account_id,user_id)
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT id ,account_id,description,amount,transaction_type
                FROM transactions where id=%s
                """,
                (transaction_id,)
                )
                row = cur.fetchone()
                return Transaction(transaction_type=row[4],amount=row[3],description=row[2],account_id=row[1],id=row[0])

    def get_transactions_by_account(
        self, account_id: str, user_id: str, page: int = 1, limit: int = 10
    ) -> list[Transaction]:
        self._account_service.get_user_account(account_id, user_id)
        offset = max(page - 1, 0) * limit
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                """
                SELECT id ,account_id,description,amount,transaction_type
                FROM transactions t JOIN accounts a on  account_id=%s a and a.user_id= userId 
                ORDER BY id
                LIMIT %s OFFSET %s
                """,
                (account_id, limit, offset)
                )
                rows = cur.fetchall()

                return [
                    Transaction(
                        id=row[0],
                        account_id=row[1],
                        description=row[2],
                        amount=row[3],
                        transaction_type=row[4],
                    )
                    for row in rows
                ]

    def get_transactions_by_user(
        self, user_id: str, page: int = 1, limit: int = 10
    ) -> list[Transaction]:
        offset = max(page - 1, 0) * limit
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT t.id, t.account_id, t.description, t.amount, t.transaction_type
                    FROM transactions t
                    JOIN accounts a ON t.account_id = a.id
                    WHERE a.user_id = %s
                    ORDER BY t.id
                    LIMIT %s OFFSET %s
                    """,
                    (user_id, limit, offset),
                )
                rows = cur.fetchall()
                return [
                    Transaction(
                        id=row[0],
                        account_id=row[1],
                        description=row[2],
                        amount=row[3],
                        transaction_type=row[4],
                    )
                    for row in rows
                ]


    def edit_transaction(
        self,
        transaction_id: str,
        amount: float,
        transaction_type: str,
        description: str,
        account_id: str,
        user_id: str,
    ) -> None:
        # validate access to new account
        self._account_service.get_user_account(account_id, user_id)

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT t.id, t.account_id, t.amount, t.transaction_type
                    FROM transactions t
                    JOIN accounts a ON t.account_id = a.id
                    WHERE t.id = %s AND a.user_id = %s
                    """,
                    (transaction_id, user_id),
                )
                old_row = cur.fetchone()
                if not old_row:
                    raise TransactionNotFoundError(transaction_id)

                old_account_id = old_row[1]
                old_amount = float(old_row[2])
                old_type = old_row[3]

                # rollback old transaction
                self._account_service.update_account_balance(
                    -old_amount,
                    old_account_id,
                    old_type,
                    user_id,
                    cur,
                )

                # apply new transaction
                self._account_service.update_account_balance(
                    amount,
                    account_id,
                    transaction_type,
                    user_id,
                    cur,
                )

                cur.execute(
                    """
                    UPDATE transactions
                    SET account_id = %s,
                        description = %s,
                        amount = %s,
                        transaction_type = %s
                    WHERE id = %s
                    RETURNING id
                    """,
                    (account_id, description, amount, transaction_type, transaction_id),
                )
                row = cur.fetchone()
                if not row:
                    raise TransactionNotFoundError(transaction_id)


    def deleteTransaction(
        self,
        user_id: str,
        transaction_id: str,
    ) -> None:
        with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        DELETE FROM transactions t
                        USING accounts a
                        WHERE t.account_id = a.id
                        AND t.id = %s
                        AND a.user_id = %s
                        RETURNING t.id, t.account_id, t.amount, t.transaction_type;
                        """,
                        (transaction_id,user_id)
                    )
                    row = cur.fetchone()
                    if not row:
                        raise TransactionNotFoundError(transaction_id)
                    self._account_service.update_account_balance(-row[2],row[1],row[3],user_id,cur)

    def get_transaction_admin(self, transaction_id: str) -> Transaction:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, account_id, description, amount, transaction_type
                    FROM transactions
                    WHERE id = %s
                    """,
                    (transaction_id,),
                )
                row = cur.fetchone()
                if not row:
                    raise TransactionNotFoundError(transaction_id)
                return Transaction(
                    id=row[0],
                    account_id=row[1],
                    description=row[2],
                    amount=row[3],
                    transaction_type=row[4],
                )

    def delete_transaction_admin(self, transaction_id: str) -> None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, account_id, amount, transaction_type
                    FROM transactions
                    WHERE id = %s
                    """,
                    (transaction_id,),
                )
                row = cur.fetchone()
                if not row:
                    raise TransactionNotFoundError(transaction_id)

                cur.execute(
                    """
                    DELETE FROM transactions
                    WHERE id = %s
                    RETURNING id
                    """,
                    (transaction_id,),
                )
                deleted = cur.fetchone()
                if not deleted:
                    raise TransactionNotFoundError(transaction_id)

                self._account_service.update_account_balance_admin(
                    -row[2],
                    row[1],
                    row[3],
                    cur,
                )
