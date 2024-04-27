from fastapi import APIRouter, Depends, status
from prisma.models import User
from prisma.errors import PrismaError
from prisma import Client
from config.db_config import get_db_connection
from config.auth_config import get_authorized_user
from utils.exceptions import (
    CustomPrismaException,
    CustomGeneralException,
    CustomRoleException,
)


router = APIRouter(prefix="/carts", tags=["Carts"])


@router.get("/")
async def get_all_carts_of_user(
    user: User = Depends(get_authorized_user), db: Client = Depends(get_db_connection)
):
    try:
        carts = await db.cart.find_many(
            where={"cart_owner_id": user.user_id},
            order={"updated_at": "desc"},
            include={"products": True},
        )
    except PrismaError as e:
        raise CustomPrismaException(str(e))
    return carts


@router.get("/{cart_id}")
async def get_single_cart(
    cart_id: str,
    user: User = Depends(get_authorized_user),
    db: Client = Depends(get_db_connection),
):
    try:
        cart = await db.cart.find_first(
            where={"AND": [{"cart_id": cart_id}, {"cart_owner_id": user.user_id}]},
            include={"products": True},
        )
        if cart is None:
            raise CustomGeneralException(
                status_code=status.HTTP_404_NOT_FOUND, error_msg="Cart not found"
            )
    except PrismaError as e:
        raise CustomPrismaException(str(e))

    return cart


@router.post("/new")
async def create_a_cart(
    user: User = Depends(get_authorized_user), db: Client = Depends(get_db_connection)
):
    try:
        new_cart = await db.cart.create(data={"cart_owner_id": user.user_id},include={"products":True})
    except PrismaError as e:
        raise CustomPrismaException(str(e))

    return new_cart


@router.put("/{cart_id}/add/{product_id}")
async def add_product_in_cart(
    cart_id: str,
    product_id: str,
    user: User = Depends(get_authorized_user),
    db: Client = Depends(get_db_connection),
):
    try:
        if(user.user_type == "SELLER"):
            raise CustomRoleException(role_can_access="ONLY_CUSTOMER")
        existing_cart = await db.cart.find_unique(
            where={"cart_id": cart_id}, include={"products": True}
        )

        if existing_cart is None:
            raise CustomGeneralException(
                status_code=status.HTTP_404_NOT_FOUND, error_msg="Cart not found"
            )

        existing_product = await db.product.find_unique(
            where={"product_id": product_id}
        )

        if existing_product is None:
            raise CustomGeneralException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_msg="Product not found. Can not add to cart.",
            )
        else:
            if existing_product.price + existing_cart.total_price > user.balance:
                raise CustomGeneralException(status_code=status.HTTP_403_FORBIDDEN,error_msg="You do not have sufficient balance.")
            if existing_product.available == False:
                raise CustomGeneralException(status_code=status.HTTP_403_FORBIDDEN,error_msg="Product is not available.")
        if existing_cart.products:
            for product in existing_cart.products:
                if product.product_id == existing_product.product_id:
                    raise CustomGeneralException(
                        status_code=status.HTTP_409_CONFLICT,
                        error_msg="A product can be added to a cart only once",
                    )

        product_price = int(existing_product.price - (existing_product.price * (existing_product.discount / 100)))

        print(product_price)

        updated_cart = await db.cart.update(
            where={"cart_id": cart_id},
            data={
                "total_price": existing_cart.total_price + product_price,
                "products": {"connect": [{"product_id": product_id}]},
            },
            include={"products": True},
        )
    except PrismaError as e:
        raise CustomPrismaException(str(e))

    return updated_cart


@router.patch("/{cart_id}/remove/{product_id}")
async def remove_product_from_cart(
    cart_id: str,
    product_id: str,
    user: User = Depends(get_authorized_user),
    db: Client = Depends(get_db_connection),
):
    try:
        existing_cart = await db.cart.find_unique(
            where={"cart_id": cart_id}, include={"products": True}
        )

        if existing_cart is None:
            raise CustomGeneralException(
                status_code=status.HTTP_404_NOT_FOUND, error_msg="Cart not found"
            )

        existing_product = await db.product.find_unique(
            where={"product_id": product_id}
        )

        if existing_product is None:
            raise CustomGeneralException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_msg="Product not found",
            )
        
        product_price = int(existing_product.price - (existing_product.price * (existing_product.discount / 100)))
        updated_cart = await db.cart.update(
            where={"cart_id": cart_id},
            data={
                "total_price": existing_cart.total_price - product_price,
                "products": {"disconnect": [{"product_id": product_id}]},
            },
            include={"products": True},
        )
        
        
    except PrismaError as e:
        raise CustomPrismaException(str(e))
    
    return updated_cart
    


@router.delete("/{cart_id}")
async def delete_cart(
    cart_id: str,
    user: User = Depends(get_authorized_user),
    db: Client = Depends(get_db_connection),
):
    try:
        existing_cart = await db.cart.find_unique(where={"cart_id": cart_id})

        if existing_cart is None:
            raise CustomGeneralException(
                status_code=status.HTTP_404_NOT_FOUND, error_msg="Cart not found"
            )
        else:
            if user.is_admin or existing_cart.cart_owner_id == user.user_id:
                await db.cart.delete(where={"cart_id": cart_id})
            else:
                raise CustomRoleException(role_can_access="OWNER")

    except PrismaError as e:
        raise CustomPrismaException(str(e))

    return {"msg": "Cart deleted"}
