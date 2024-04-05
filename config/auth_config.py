from datetime import datetime, timedelta, timezone
from typing import Annotated

from config.db_config import get_db_connection
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from prisma.errors import PrismaError

from config.settings import Settings
from prisma import Client
from routes.auth_route.model import LoginCredentials
from utils.exceptions import (CustomAuthorizationException,
                              CustomGeneralException, CustomPrismaException)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')






async def validate_login_credentials(login_credentials:LoginCredentials, token_expire_time:timedelta,db:Client):
    try:
        user = await db.user.find_first(where={
            'email':login_credentials.email
        })
        if not user:
            raise CustomAuthorizationException(error_msg="Invalid login credentials provided. User does not exist.")
        if user.password != login_credentials.password:
            raise CustomAuthorizationException(error_msg="Invalid password provided. Please try again.")
        
        token_expires_at = datetime.now(timezone.utc) + token_expire_time or timedelta(hours=24)

        data_to_encode = {
            "sub":user.email,
            "exp": token_expires_at
        }
        token = await generate_jwt_token(data_to_encode)
        return token
    except PrismaError as e:
        raise CustomPrismaException(error_msg=str(e))
        
        
    
secret_key = Settings.secret_key

async def generate_jwt_token(data:dict):
    try:
        token = jwt.encode(data,key=secret_key,algorithm="HS256")
    except JWTError as e:
        raise CustomGeneralException(status_code=500, error_msg=str(e))
    
    return token



async def get_authorized_user(token: Annotated[str, Depends(oauth2_scheme)], db:Client=Depends(get_db_connection)):
    try:
        payload = jwt.decode(token,secret_key, algorithms=["HS256"])
        email = payload.get("sub")
        if email is None:
            raise CustomAuthorizationException(error_msg="Could not validate credentials. User not logged in.")
        
    except JWTError:
        raise CustomAuthorizationException(error_msg="Could not validate credentials. User not logged in.")
    
    user = await db.user.find_first(where={
        "email":email
    })
    if user is None:
        raise CustomAuthorizationException(error_msg="Could not validate credentials. Invalid email address provided.")
    return user

