

from Service.AccountService import AccountService
from Service.TransactionService import TransactionService
from Service.UserService import UserService


class OrchestratorService ():
    def __init__ (self, userService: UserService, accountService: AccountService, transactionService:TransactionService):
        self._userService = userService
        self._accountService = accountService
        self._transactionService = transactionService
    
    def deleteUser (self, userId)->None:
        user_accounts = self._accountService.get_all_accounts_of_user(userId)

        for account in user_accounts:
            self._transactionService.deleteTransactionsOfAccount(userId,account.id)
        self._accountService.deleteUsersAccount(userId)
        self._userService.delete_user(userId)
    
    def deleteAccount (self, userId:str, accountId:str)->None:
        self._transactionService.deleteTransactionsOfAccount(userId,accountId)
        self._accountService.deleteAccount(userId,accountId)
            
