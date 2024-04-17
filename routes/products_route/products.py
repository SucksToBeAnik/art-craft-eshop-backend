from fastapi import APIRouter, Depends, status, Query
from prisma.errors import PrismaError
from prisma.models import User
from typing import Optional, Annotated

from config.auth_config import get_authorized_user
from config.db_config import get_db_connection
from prisma import Client
from utils.exceptions import (CustomAuthorizationException,
                              CustomGeneralException, CustomPrismaException,
                              CustomRoleException)

from .model import CreateProduct

router = APIRouter(
    prefix="/products",
    tags=['Products']
)

@router.get('/')
async def get_all_products(limit: Annotated[Optional[int], Query(gt=0)] = None,db: Client = Depends(get_db_connection)):
    try:
        products = await db.product.find_many(take=limit)
    except PrismaError as e:
        raise CustomPrismaException(error_msg=str(e))
    return products

@router.get('/shop/{shop_id}')
async def get_all_products_from_shop(shop_id: str, db:Client = Depends(get_db_connection)):
    try:
        products = await db.product.find_many(where={
            "owner_shop_id":shop_id
        })
    except PrismaError as e:
        raise CustomPrismaException(error_msg=str(e))
    return products
    


@router.post('/new', status_code=status.HTTP_201_CREATED)
async def create_a_product(product_data: CreateProduct, db:Client = Depends(get_db_connection),user:User = Depends(get_authorized_user)):
    if(user.is_admin or user.user_type == "SELLER"):
        pass
    else:
        raise CustomRoleException(role_can_access="SELLER")
    
    try:
        new_product = await db.product.create(data={
            "name":product_data.name,
            "description": product_data.description,
            "manufacturer": product_data.manufacturer,
            "images": product_data.images,
            "price":product_data.price,
            "available":product_data.available,
            "discount":product_data.discount,
            "product_type":product_data.product_type,
            "owner_shop_id": product_data.owner_shop_id
        })
    except PrismaError as e:
        raise CustomPrismaException(error_msg=str(e))
    
    return new_product