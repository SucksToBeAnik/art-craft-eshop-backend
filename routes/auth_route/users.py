from datetime import timedelta
from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from prisma.errors import PrismaError

from config.auth_config import validate_login_credentials, get_authorized_user
from config.db_config import get_db_connection
from config.settings import Settings
from prisma import Client
from prisma.models import User as UserSchema
from utils.exceptions import CustomPrismaException, CustomGeneralException, CustomRoleException
from config.auth_config import get_authorized_user

from .model import LoginCredentials, User

from config.settings import Settings

router = APIRouter(
    prefix="/auth",
    tags=['Auth']
)



@router.get('/users',)
async def get_all_users(db: Client = Depends(get_db_connection)):
    try:
        users = await db.user.find_many()
    except PrismaError as e:
        raise CustomPrismaException(error_msg=str(e))
    
    return users


@router.get('/users/{id}',)
async def get_specific_user(id:str,db: Client = Depends(get_db_connection)):
    try:
        user = await db.user.find_first(where={
            "user_id":id
        })
        if user is None:
            raise CustomGeneralException(status_code=status.HTTP_404_NOT_FOUND, error_msg="User does not exist")
    except PrismaError as e:
        raise CustomPrismaException(error_msg=str(e))
    
    return user



@router.get('/me')
async def get_active_user(user = Depends(get_authorized_user)):
    return user



@router.post('/register', status_code=status.HTTP_201_CREATED)
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
    
    return new_user

@router.post("/login")
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Client = Depends(get_db_connection)):
    credentials = LoginCredentials(email=form_data.username, password=form_data.password)

    token = await validate_login_credentials(credentials,timedelta(hours=1), db)
        
    return {
        "access_token":token
    }


@router.patch('/me/switch')
async def switch_user_account_type(db: Client = Depends(get_db_connection), user: UserSchema = Depends(get_authorized_user)):
    if user.user_type == "CUSTOMER":
        new_user_type =   "SELLER"  
    else:
        new_user_type = "CUSTOMER"
        
    try:
        updated_user = await db.user.update(where={
            "user_id":user.user_id
        }, data={
            "user_type": new_user_type
        })
        if not updated_user:
            raise CustomGeneralException(status_code=status.HTTP_404_NOT_FOUND, error_msg="Could not find user account")
    except PrismaError as e:
        raise CustomPrismaException(str(e))
    
    return updated_user

@router.delete("/delete/{user_id}")
async def delete_user(user_id: str, db:Client = Depends(get_db_connection), user:UserSchema = Depends(get_authorized_user)):
    if(user_id != user.user_id and not user.is_admin):
        raise CustomRoleException(role_can_access="OWNER")
    try:
        deleted_user = await db.user.delete(where={
            "user_id": user_id
        })
    except PrismaError as e:
        raise CustomPrismaException(str(e))
    
    return {
        "deleted_user": deleted_user
    }

