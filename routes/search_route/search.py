from typing import Annotated

from fastapi import APIRouter, Depends, Path
from prisma.errors import PrismaError

from config.db_config import get_db_connection
from prisma import Client
from utils.exceptions import CustomPrismaException

router = APIRouter(prefix="/search")


@router.get("/products/{term}")
async def search_products(
    term: Annotated[str, Path(min_length=3)], db: Client = Depends(get_db_connection)
):
    try:
        products = await db.product.find_many(where={"name": {"contains": term}})
    except PrismaError as e:
        raise CustomPrismaException(str(e))

    return products


@router.get("/shops/{term}")
async def search_shops(
    term: Annotated[str, Path(min_length=3)], db: Client = Depends(get_db_connection)
):
    try:
        shops = await db.shop.find_many(where={"name": {"contains": term}})
    except PrismaError as e:
        raise CustomPrismaException(str(e))

    return shops
