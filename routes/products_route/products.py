from fastapi import APIRouter, Depends, status, Query
from prisma.errors import PrismaError
from prisma.models import User
from typing import Optional, Annotated

from config.auth_config import get_authorized_user
from config.db_config import get_db_connection
from prisma import Client
from prisma.types import UserUpdateManyWithoutRelationsInput

from utils.exceptions import (
    CustomAuthorizationException,
    CustomGeneralException,
    CustomPrismaException,
    CustomRoleException,
)

from .model import UpdateProduct, CreateProduct

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/")
async def get_all_products(
    limit: Annotated[Optional[int], Query(gt=0)] = None,
    db: Client = Depends(get_db_connection),
):
    try:
        products = await db.product.find_many(take=limit)
    except PrismaError as e:
        raise CustomPrismaException(error_msg=str(e))
    return products


@router.get("/shop/{shop_id}")
async def get_all_products_from_shop(
    shop_id: str, db: Client = Depends(get_db_connection)
):
    try:
        products = await db.product.find_many(where={"owner_shop_id": shop_id})
    except PrismaError as e:
        raise CustomPrismaException(error_msg=str(e))
    return products


@router.get("/owner/{owner_id}")
async def get_all_products_from_user(
    owner_id: str, db: Client = Depends(get_db_connection)
):
    try:
        owned_shops = await db.shop.find_many(
            where={"owner_id": owner_id}, include={"products": True}
        )
        owned_products = [shop.products for shop in owned_shops if shop.products]
    except PrismaError as e:
        raise CustomPrismaException(error_msg=str(e))

    return owned_products


@router.post("/new", status_code=status.HTTP_201_CREATED)
async def create_a_product(
    product_data: CreateProduct,
    db: Client = Depends(get_db_connection),
    user: User = Depends(get_authorized_user),
):
    if user.is_admin or user.user_type == "SELLER":
        pass
    else:
        raise CustomRoleException(role_can_access="SELLER")

    try:
        new_product = await db.product.create(
            data={
                "name": product_data.name,
                "description": product_data.description,
                "manufacturer": product_data.manufacturer,
                "images": product_data.images,
                "price": product_data.price,
                "discount": product_data.discount,
                "product_type": product_data.product_type,
                "owner_shop_id": product_data.owner_shop_id,
            }
        )
    except PrismaError as e:
        raise CustomPrismaException(error_msg=str(e))

    return new_product



@router.put("/{product_id}")
async def update_product(
    product_id: str,
    product_data: UpdateProduct,
    db: Client = Depends(get_db_connection),
    user: User = Depends(get_authorized_user),
):
    if user.is_admin:
        pass
    else:
        try:
            existing_product = await db.product.find_first_or_raise(
                where={"product_id": product_id}
            )
            user_shops = await db.shop.find_many(where={"owner_id": user.user_id})

            if user_shops:
                user_shops_id = [shop.shop_id for shop in user_shops]
                if existing_product.owner_shop_id not in user_shops_id:
                    raise CustomRoleException(role_can_access="OWNER")

            else:
                raise CustomGeneralException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    error_msg="You do not own any shops. Please create one.",
                )

            updated_product = await db.product.update(
                where={"product_id": product_id},
                data={
                    "name": product_data.name or existing_product.name,
                    "description": product_data.description
                    or existing_product.description,
                    "manufacturer": product_data.manufacturer
                    or existing_product.manufacturer,
                    "images": product_data.images or existing_product.images,
                    "price": product_data.price or existing_product.price,
                    "discount": product_data.discount or existing_product.discount,
                    "product_type": product_data.product_type
                    or existing_product.product_type,
                    "available": product_data.available or existing_product.available,
                },
            )

        except PrismaError as e:
            raise CustomPrismaException(error_msg=str(e))

        return updated_product


@router.put("/buy/{product_id}")
async def buy_a_product(product_id:str):
    pass



@router.patch("/favourites/{product_id}")
async def add_product_to_favourite(
    product_id: str,
    db: Client = Depends(get_db_connection),
    user: User = Depends(get_authorized_user),
):
    try:
        existing_product = await db.product.find_first_or_raise(
            where={"product_id": product_id}
        )
        user_with_favourite_products = await db.user.find_unique_or_raise(where={
            "user_id":user.user_id
        },include={
            "favourite_products":True
        })

        product_is_already_favourite = False
        if user_with_favourite_products.favourite_products:
            for fav_product in user_with_favourite_products.favourite_products:
                if fav_product.product_id == existing_product.product_id:
                    product_is_already_favourite = True
        if product_is_already_favourite:
            raise CustomGeneralException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                error_msg="Product is already added to favourite",
            )
        else:
            await db.product.update(
                where={"product_id": product_id},
                data={"favourited_by": {"connect": [{"user_id": user.user_id}]}},
            )

    except PrismaError as e:
        raise CustomPrismaException(str(e))

    return {
        "msg": "Added to favourite",
    }




@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str, db: Client = Depends(get_db_connection), user: User = Depends(get_authorized_user), products = Depends(get_all_products_from_user)):
    try:
        existing_product = await db.product.find_unique(where={
            "product_id":product_id
        })

        if not existing_product:
            raise CustomPrismaException(error_msg="Product does not exist", status_code=status.HTTP_404_NOT_FOUND)


        user_can_delete = False
        for shop_products in products:
            if existing_product in shop_products:
                user_can_delete = True
            
        if user_can_delete:
            await db.product.delete(where={
                "product_id":existing_product.product_id
            })
        else:
            raise CustomRoleException(role_can_access="OWNER")
        
    except PrismaError as e:
        raise CustomPrismaException(str(e))        

