from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from prisma.errors import PrismaError

from config.auth_config import validate_login_credentials, get_authorized_user
from config.db_config import get_db_connection
from config.settings import Settings
from prisma import Client
from utils.exceptions import CustomPrismaException

from .model import LoginCredentials, User

from config.settings import Settings

router = APIRouter(
    prefix="/auth",
    tags=['Auth']
)


@router.get('/users',dependencies=[Depends(get_authorized_user)])
async def get_all_users(db: Client = Depends(get_db_connection)):
    
    try:
        users = await db.user.find_many()
    except PrismaError as e:
        raise CustomPrismaException(error_msg=str(e))
    
    return users

@router.post('/users/new')
async def register_new_user(user_data:User, db:Client = Depends(get_db_connection)):
    is_admin = False
    print(Settings.admin_emails)
    for email in Settings.admin_emails:
        if email == user_data.email:
            is_admin = True
    
    
    try:
        new_user = await db.user.create(data={
            'full_name':user_data.full_name,
            'password':user_data.password,
            'bio':user_data.bio,
            'email':user_data.email,
            'image':user_data.image,
            "address":user_data.address,
            'phone_number':user_data.phone_number,
            'is_admin': is_admin

        })
    except PrismaError as e:
        raise CustomPrismaException(error_msg=str(e))
    
    return {
        "msg":"Registration completed!",
        "user": new_user
    }

@router.post("/login")
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Client = Depends(get_db_connection)):
    credentials = LoginCredentials(email=form_data.username, password=form_data.password)

    token = await validate_login_credentials(credentials,timedelta(hours=1), db)

    return {
        "access_token":token
    }

