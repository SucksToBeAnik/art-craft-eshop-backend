from fastapi import status
from typing import Literal

class CustomGeneralException(Exception):
    def __init__(self, error_msg:str, status_code:int):
        self.status_code = status_code
        self.error_msg = error_msg
    


class CustomPrismaException(Exception):
    def __init__(self, error_msg:str, status_code:int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.status_code = status_code
        self.error_msg = error_msg


class CustomAuthorizationException(Exception):
    def __init__(self, error_msg:str, status_code:int = status.HTTP_401_UNAUTHORIZED):
        self.status_code = status_code
        self.error_msg = error_msg






RoleCanAccess = Literal["CUSTOMER","SELLER","OWNER"]

class CustomRoleException(Exception):
    def __init__(self, role_can_access: RoleCanAccess, status_code:int = status.HTTP_403_FORBIDDEN):
        self.status_code = status_code
        self.role_can_access = role_can_access

        if self.role_can_access == "CUSTOMER":
            self.error_msg = "Only an Admin or a Customer can perform this action. Switch to customer account."
        elif self.role_can_access == "SELLER":
            self.error_msg = "Only an Admin or a Seller can perform this action. Switch to seller account."
        elif self.role_can_access == "OWNER":
            self.error_msg = "Only an Admin or its owner can perform this action"

