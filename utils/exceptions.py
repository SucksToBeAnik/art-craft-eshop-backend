from fastapi import status

class CustomPrismaException(Exception):
    def __init__(self,  error_msg:str, status_code:int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.status_code = status_code
        self.error_msg = error_msg
