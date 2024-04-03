from fastapi import APIRouter


router = APIRouter(
    prefix="/reviews",
    tags=['Reviews']
)


@router.get('/')
async def get_all_carts():
    return 'There are currently no reviews'