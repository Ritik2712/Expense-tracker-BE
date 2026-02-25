from uuid import UUID
from Schemas.User import User
from exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from utils.db import get_connection
from utils.security import hash_password, verify_password
from psycopg2.errors import UniqueViolation


class UserService:


    def get_user(self, id: str) -> User:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, role
                    FROM users
                    WHERE id = %s
                    """,
                    (id,)
                )
                row = cur.fetchone()
                if(not row):
                    raise UserNotFoundError(id)
                new_user = User(name=row[1], role=row[2], id=row[0])
                return new_user

    def update_user(self, id: str, name: str) -> User:
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:

                    cur.execute(
                        """
                    UPDATE users
                    SET name = %s
                    WHERE id = %s
                    RETURNING id, name, role
                    """,
                    (name,id)
                    )
                    row = cur.fetchone()
                    if not row:
                        raise UserNotFoundError(id)
                    new_user = User(name=row[1], role=row[2], id=row[0])
                    return new_user
        except UniqueViolation as e:
            raise UserAlreadyExistsError(name)


    def delete_user(self, id: str) -> None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM users
                    WHERE id = %s
                    RETURNING id
                    """,
                    (id,),
                )
                row = cur.fetchone()
                if not row:
                    raise UserNotFoundError(id)

    def get_all_users(self, page: int = 1, limit: int = 10) -> list[User]:  # development only
        offset = max(page - 1, 0) * limit
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, role
                    FROM users
                    ORDER BY id
                    LIMIT %s OFFSET %s
                    """
                    ,
                    (limit, offset),
                )

                rows = cur.fetchall()

                if(not rows):
                    raise UserNotFoundError("No")
                return [
                    User(id=row[0], name=row[1], role=row[2])
                    for row in rows
                ]
