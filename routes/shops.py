from fastapi import APIRouter


router = APIRouter(
    prefix="/shops",
    tags=['Shops']
)


@router.get('/')
async def get_all_carts():
    return 'There are currently no shops'