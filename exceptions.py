class UserError(Exception):
    """Base class for all user-related errors."""
    pass


class InvalidUserType(UserError):
    def __init__(self, message:str):
        super().__init__(
            f"User type {message} is invalid"
        )


class UserAlreadyExistsError(UserError):
    def __init__(self, name: str):
        super().__init__(f"User with name '{name}' already exists")


class UserNotFoundError(UserError):
    def __init__(self, user_id: str):
        super().__init__(f"No user found with id '{user_id}'")


class InvalidCredentialsError(UserError):
    def __init__(self):
        super().__init__("Invalid credentials")



class AccountError(Exception):
    """Base class for all account-related errors."""
    pass

class InvalidAccountError(AccountError):
    def __init__(self, message:str):
        super().__init__(message)

class AccountNotFoundError(AccountError):
    def __init__(self, account_id: str):
        super().__init__(f"No account found with id '{account_id}'")


class AccountAccessDeniedError(AccountError):
    def __init__(self, account_id: str, user_id: str):
        super().__init__(
            f"User '{user_id}' has no access to account '{account_id}'"
        )


class InvalidTransactionTypeError(AccountError):
    def __init__(self, transaction_type: str):
        super().__init__(
            f"Invalid transaction type '{transaction_type}'. Expected 'Income' or 'Expense'"
        )
class TransactionError(Exception):
    """Base class for all transaction-related errors."""
    pass


class TransactionNotFoundError(TransactionError):
    def __init__(self, transaction_id: str):
        super().__init__(f"Transaction '{transaction_id}' not found")


class TransactionAccountMismatchError(TransactionError):
    def __init__(self, transaction_id: str, account_id: str):
        super().__init__(
            f"Transaction '{transaction_id}' does not belong to account '{account_id}'"
        )

class InvalidTransaction(TransactionError):
    def __init__(self, message:str):
        super().__init__(
            f"Transaction failed because {message}"
        )
