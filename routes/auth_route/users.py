from fastapi import APIRouter, Depends
from prisma import Client
from prisma.errors import PrismaError
from config.db_config import get_db_connection
from .model import User
from utils.exceptions import CustomPrismaException


router = APIRouter(
    prefix="/auth",
    tags=['Auth']
)


@router.get('/users')
async def get_all_users():
    return 'There are currently no users'

@router.post('/users/new')
async def register_new_user(user_data:User, db:Client = Depends(get_db_connection)):
    try:
        new_user = await db.user.create(data={
            'full_name':user_data.full_name,
            'password':user_data.password,
            'bio':user_data.bio,
            'email':user_data.email,
            'image':user_data.image,
            "address":user_data.address,
            'phone_number':user_data.phone_number

        })
    except PrismaError as e:
        raise CustomPrismaException(error_msg=str(e))
    
    return {
        "msg":"Registration completed!",
        "user": new_user
    }