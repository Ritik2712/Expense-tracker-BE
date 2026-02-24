from datetime import datetime, timezone
import uuid
from dataclasses import dataclass, field

from exceptions import InvalidTransaction

@dataclass
class Transaction():
    transaction_type:str
    amount:int
    description:str
    account_id:str
    date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id:str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        if self.amount<0:
            raise InvalidTransaction("Amount cannot be negative")
        elif self.transaction_type != "Expense" and self.transaction_type != "Income" and self.transaction_type != "Cross":
            raise InvalidTransaction("Transaction type should be Expense or Income or Cross")