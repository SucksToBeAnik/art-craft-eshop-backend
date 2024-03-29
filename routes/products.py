from fastapi import APIRouter


router = APIRouter(
    prefix="/products",
    tags=['Products']
)


@router.get('/')
async def get_all_carts():
    return 'There are currently no products'