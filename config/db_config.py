from prisma import Prisma

async def get_db_connection():
    db = Prisma()

    try:
        await db.connect()
        yield db
    finally:
        await db.disconnect()
