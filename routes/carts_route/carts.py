from fastapi import APIRouter


router = APIRouter(
    prefix="/carts",
    tags=['Carts']
)


@router.get('/')
async def get_all_carts():
    return 'There are currently no carts'