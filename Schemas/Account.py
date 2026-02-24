import uuid
from dataclasses import dataclass, field

from exceptions import InvalidAccountError


@dataclass
class Account():
    name:str
    user_id:str
    balance:float =field(default=0)
    id:str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        if self.balance<0:
            raise InvalidAccountError("Balance cannot be negative")