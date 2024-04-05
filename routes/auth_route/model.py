from pydantic import BaseModel, Field, EmailStr, model_validator
from enum import Enum
from typing import Annotated


class UserType(Enum):
    customer = 'CUSTOMER'
    seller = 'SELLER'

class User(BaseModel):
    full_name: Annotated[str, Field(...,min_length=2)]
    password: str
    bio: str | None = None
    email: EmailStr
    image: str | None = None
    address: str | None = None
    phone_number: list[str] = []
    user_type: UserType = UserType.customer

    @model_validator(mode='after')
    def validate_password(self):
        special_chars = ['@','#','$','&','!']
        sp_count = 0

        for char in self.password:
            if char in special_chars:
                sp_count +=1

        if len(self.password) < 5:
            raise ValueError("Your password should at least be 5 characters long!")
        
        if sp_count == 0:
            raise ValueError('Your password should contain atleast one of the following special characters: [@, #, $, &, !]')
        
        return self

class LoginCredentials(BaseModel):
    email: EmailStr
    password: str