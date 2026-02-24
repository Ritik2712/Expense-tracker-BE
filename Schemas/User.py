import uuid
from dataclasses import dataclass, field

from exceptions import InvalidUserType

@dataclass
class User():
    name:str
    role: str
    id:str 

    def __post_init__(self):
        if( self.role!="admin"and self.role != "user"):
            raise InvalidUserType(self.role)