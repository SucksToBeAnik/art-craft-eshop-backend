from fastapi import APIRouter


router = APIRouter(
    prefix="/orders",
    tags=['Orders']
)


@router.get('/')
async def get_all_carts():
    return 'There are currently no orders'