from uuid import UUID

from Schemas.Account import Account
from exceptions import (
    AccountNotFoundError,
    AccountAccessDeniedError,
    InvalidTransactionTypeError,
)
from utils.db import get_connection


class AccountService:
    def __init__(self):
        pass

    def create_account(self, user_id: str, name: str) -> Account:
        with get_connection() as conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    INSERT INTO accounts (name, user_id, balance)
                    VALUES (%s, %s, %s)
                    RETURNING id, name, user_id, balance
                    """,
                    (name, user_id, 0),
                )
                row = cur.fetchone()
                return Account(
                    id=row[0],
                    name=row[1],
                    user_id=row[2],
                    balance=row[3],
                )

    def get_all_accounts_of_user(
        self, user_id: str, page: int = 1, limit: int = 10
    ) -> list[Account]:
        offset = max(page - 1, 0) * limit

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, user_id, balance
                    FROM accounts
                    WHERE user_id = %s
                    ORDER BY id
                    LIMIT %s OFFSET %s
                    """,
                    (user_id, limit, offset),
                )
                rows = cur.fetchall()
                return [
                    Account(
                        id=row[0],
                        name=row[1],
                        user_id=row[2],
                        balance=row[3],
                    )
                    for row in rows
                ]

    def update_account(
        self,
        user_id: str,
        balance: float,
        account_id: str,
        account_name: str,
    ) -> None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE accounts
                    SET name = %s, balance = %s
                    WHERE id = %s and user_id = %s
                    RETURNING id, name, user_id, balance
                    """,
                    (account_name, balance, account_id,user_id),
                )
                row = cur.fetchone()
                if not row:
                    raise AccountNotFoundError(account_id)

    def get_user_account(self, account_id: str, user_id: str) -> Account:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, user_id, balance
                    FROM accounts
                    WHERE id = %s and user_id = %s
                    """,
                    (account_id,user_id),
                )
                row = cur.fetchone()
                if not row:
                    raise AccountNotFoundError(account_id)
                return Account(
                    id=row[0],
                    name=row[1],
                    user_id=row[2],
                    balance=row[3],
                )

    def update_account_balance(
        self,
        amount: float,
        account_id: str,
        transaction_type: str,
        user_id:str,
        cur
    ) -> None:
        if transaction_type == "Expense":
            delta = -amount
        elif transaction_type == "Income":
            delta = amount
        else:
            raise InvalidTransactionTypeError(transaction_type)

        
        cur.execute(
            """
            UPDATE accounts
            SET balance = balance + %s
            WHERE id = %s and user_id = %s
            RETURNING id, balance
            """,
            (delta, account_id,user_id),
        )
        row = cur.fetchone()
        if not row:
            raise AccountNotFoundError(account_id)

    def deleteUsersAccount(self, user_id: str) -> None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM accounts
                    WHERE user_id = %s
                    """,
                    (user_id,),
                )

    def deleteAccount(self, user_id: str, account_id: str) -> None:
        self.get_user_account(account_id, user_id)
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM accounts
                    WHERE id = %s and user_id = %s
                    RETURNING id
                    """,
                    (account_id,user_id),
                )
                row = cur.fetchone()
                if not row:
                    raise AccountNotFoundError(account_id)

    def get_account_admin(self, account_id: str) -> Account:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, user_id, balance
                    FROM accounts
                    WHERE id = %s
                    """,
                    (account_id,),
                )
                row = cur.fetchone()
                if not row:
                    raise AccountNotFoundError(account_id)
                return Account(
                    id=row[0],
                    name=row[1],
                    user_id=row[2],
                    balance=row[3],
                )

    def get_all_accounts_admin(self) -> list[Account]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, user_id, balance
                    FROM accounts
                    ORDER BY id
                    """
                )
                rows = cur.fetchall()
                return [
                    Account(
                        id=row[0],
                        name=row[1],
                        user_id=row[2],
                        balance=row[3],
                    )
                    for row in rows
                ]

    def delete_account_admin(self, account_id: str) -> None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM accounts
                    WHERE id = %s
                    RETURNING id
                    """,
                    (account_id,),
                )
                row = cur.fetchone()
                if not row:
                    raise AccountNotFoundError(account_id)

    def update_account_balance_admin(
        self,
        amount: float,
        account_id: str,
        transaction_type: str,
        cur,
    ) -> None:
        if transaction_type == "Expense":
            delta = -amount
        elif transaction_type == "Income":
            delta = amount
        else:
            raise InvalidTransactionTypeError(transaction_type)

        cur.execute(
            """
            UPDATE accounts
            SET balance = balance + %s
            WHERE id = %s
            RETURNING id, balance
            """,
            (delta, account_id),
        )
        row = cur.fetchone()
        if not row:
            raise AccountNotFoundError(account_id)
