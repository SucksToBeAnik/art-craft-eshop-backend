from fastapi import HTTPException
from prisma import Prisma
from prisma.errors import PrismaError

from prisma.engine.errors import EngineConnectionError
from utils.exceptions import CustomPrismaException

async def get_db_connection():
    db = Prisma()
    try:
        await db.connect()
        yield db
    except PrismaError as e:
        raise CustomPrismaException(error_msg="Something went wrong while connecting to the database. Please try again.")
    finally:
        if db.is_connected():
            await db.disconnect()
