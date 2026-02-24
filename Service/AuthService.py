from uuid import UUID
from Schemas.User import User
from exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
)
from utils.db import get_connection
from utils.security import hash_password, verify_password
from psycopg2.errors import UniqueViolation


class AuthService:

    def register_user(self, name: str ,password: str,role:str) -> User:
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    hashed_passowrd = hash_password(password)
                    cur.execute(
                        """
                        INSERT INTO
                        users (name,role,password)
                        VALUES (%s,%s,%s)
                        RETURNING id, name,role
                        """,
                        ( name,role ,hashed_passowrd)
                    )
                    row = cur.fetchone()
                    new_user = User(id=row[0],name=row[1],role=row[2])
                    if(not row):
                        return []

                    return new_user
        except UniqueViolation as e:
            raise UserAlreadyExistsError(name)
        


    def login_user(self, name: str, password: str) -> User:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id,name,password,role FROM users
                    WHERE name = %s
                    """,
                    (name,),
                )
                row = cur.fetchone()
                if not row or not verify_password(password, row[2]):
                    raise InvalidCredentialsError()
                return User(id=row[0], name=row[1],role=row[3])
                
