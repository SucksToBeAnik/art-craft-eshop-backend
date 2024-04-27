from fastapi import APIRouter, Depends, status
from prisma import Client
from prisma.models import User
from prisma.errors import PrismaError
from config.db_config import get_db_connection
from config.auth_config import get_authorized_user

from utils.exceptions import CustomPrismaException, CustomRoleException, CustomGeneralException


router = APIRouter(
    prefix="/orders",
    tags=['Orders']
)


@router.get('/')
async def get_all_orders(db: Client =Depends(get_db_connection), user: User=Depends(get_authorized_user)):
    try:
        orders = await db.order.find_many(where={
            "order_owner_id":user.user_id
        })
            
    
    except PrismaError as e:
        raise CustomPrismaException(str(e))
    
    return orders



@router.post('/new/{cart_id}')
async def create_order(cart_id:str,db: Client =Depends(get_db_connection), user: User=Depends(get_authorized_user)):
    try:
        # check seller or customer
        if(user.user_type == "SELLER"):
            raise CustomRoleException(role_can_access="ONLY_CUSTOMER")
        # check cart exist
        cart = await db.cart.find_unique(where={
            'cart_id':cart_id
        },
        include={
            "products":True
        }
        )

        if  cart is None:
            raise CustomGeneralException(status_code=status.HTTP_404_NOT_FOUND, error_msg="Cart not found")
        
        if cart.products:
            if cart.total_price <= user.balance:
                for prod in cart.products:
                    await db.user.update(
                        where={
                            "user_id":user.user_id
                        },
                        data={
                            "bought_products":{
                                "connect":[
                                    {"product_id":prod.product_id}
                                ]
                            },
                            "balance":user.balance - prod.price
                        }
                    )

                    product_shop = await db.shop.find_unique(where={"shop_id":prod.owner_shop_id})

                    if product_shop:
                        product_shop_owner = await db.user.find_unique(where={"user_id":product_shop.owner_id})
                        if product_shop_owner:
                            await db.user.update(where={"user_id":product_shop_owner.user_id},data={
                                "balance": product_shop_owner.balance + prod.price
                            })
                    order = await db.order.create(data={
                        "owner_cart_id":cart.cart_id,
                        "order_owner_id":user.user_id
                    })
            else:
                raise CustomGeneralException(status_code=status.HTTP_403_FORBIDDEN,error_msg="You do not have sufficient balance.")
        else:
            raise CustomGeneralException(status_code=status.HTTP_403_FORBIDDEN,error_msg="Cart is empty")
    except PrismaError as e:
        raise CustomPrismaException(str(e))
    
    return order