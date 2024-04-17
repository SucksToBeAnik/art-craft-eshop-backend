from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, status
from prisma.errors import PrismaError
from prisma.models import User

from config.auth_config import get_authorized_user
from config.db_config import get_db_connection
from prisma import Client
from utils.exceptions import (CustomGeneralException, CustomPrismaException,
                              CustomRoleException)

from .model import Shop, UpdateShop

router = APIRouter(prefix="/shops", tags=["Shops"])


@router.get("/")
async def get_all_shops(
    limit: Annotated[Optional[int], Query(gt=0, lt=50)] = None,
    db: Client = Depends(get_db_connection),
):
    try:
        shops = await db.shop.find_many(take=limit, include={
            "owner":True
        })
    except PrismaError as e:
        raise CustomPrismaException(error_msg=str(e))
    return shops


@router.get("/{shop_id}")
async def get_shop_by_id(shop_id: str, db: Client = Depends(get_db_connection)):
    try:
        shop = await db.shop.find_first(where={"shop_id": shop_id})
        if shop is None:
            raise CustomGeneralException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_msg="Invalid shop id provided. Shop does not exist!",
            )
    except PrismaError as e:
        raise CustomPrismaException(str(e))


@router.get("/{shop_name}")
async def get_shop_by_name(shop_name: str, db: Client = Depends(get_db_connection)):
    try:
        shop = await db.shop.find_first(where={"name": shop_name})
        if shop is None:
            raise CustomGeneralException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_msg="Invalid shop name provided. Shop does not exist!",
            )
    except PrismaError as e:
        raise CustomPrismaException(str(e))


@router.get("/owner/{user_id}")
async def get_specific_user_shops(
    user_id: str, db: Client = Depends(get_db_connection)
):
    try:
        shops = await db.user.find_first_or_raise(
            where={"user_id": user_id}, include={"shops": True}
        )
    except PrismaError as e:
        raise CustomPrismaException(error_msg=str(e))

    return shops


@router.post("/new", status_code=status.HTTP_201_CREATED)
async def create_a_shop(
    shop_data: Shop,
    db: Client = Depends(get_db_connection),
    user: User = Depends(get_authorized_user),
):
    if shop_data.owner_id is None:
        shop_data.owner_id = user.user_id

    if user.is_admin or user.user_type == "SELLER":
        pass
    else:
        raise CustomRoleException(role_can_access="SELLER")

    try:
        new_shop = await db.shop.create(
            data={
                "name": shop_data.name,
                "description": shop_data.description,
                "location": shop_data.location,
                "website": shop_data.website,
                "owner_id": shop_data.owner_id,
            },
            include={"owner": True},
        )
    except PrismaError as e:
        raise CustomPrismaException(error_msg=str(e))

    return new_shop



@router.put("/{id}")
async def update_a_shop(
    id: str,
    shop_data: UpdateShop,
    db: Client = Depends(get_db_connection),
    user: User = Depends(get_authorized_user),
):
    try:
        existing_shop = await db.shop.find_first(where={"shop_id": id})

        if existing_shop is None:
            raise CustomGeneralException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_msg="Invalid shop id provided. Shop does not exist!",
            )

        if user.is_admin or user.user_id == existing_shop.owner_id:
            pass
        else:
            raise CustomRoleException(role_can_access="OWNER")
        updated_shop = await db.shop.update(
            where={"shop_id": id},
            data={
                "name": shop_data.name or existing_shop.name,
                "description": shop_data.description or existing_shop.description,
                "location": shop_data.location or existing_shop.location,
                "website": shop_data.website or existing_shop.website,
            },
        )

    except PrismaError as e:
        raise CustomPrismaException(error_msg=str(e))

    return updated_shop


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_shop(
    id: str,
    db: Client = Depends(get_db_connection),
    user: User = Depends(get_authorized_user),
):
    try:
        existing_shop = await db.shop.find_first(where={"shop_id": id})
        if existing_shop is None:
            raise CustomGeneralException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_msg="Invalid shop id provided. Shop does not exist!",
            )
        if user.is_admin or user.user_id == existing_shop.owner_id:
            pass
        else:
            raise CustomRoleException(role_can_access="OWNER")
        deleted_shop = await db.shop.delete(where={"shop_id": id})

    except PrismaError as e:
        raise CustomPrismaException(error_msg=str(e))

    return deleted_shop
