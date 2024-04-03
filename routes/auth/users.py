from fastapi import APIRouter


router = APIRouter(
    prefix="/users",
    tags=['Users']
)


@router.get('/')
async def get_all_carts():
    return 'There are currently no users'