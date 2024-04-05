import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException, Request, status

from routes.auth_route import users
from routes.carts_route import carts
from routes.orders_route import orders
from routes.products_route import products
from routes.reviews_route import reviews
from routes.shops_route import shops

from utils.exceptions import (
    CustomGeneralException,
    CustomPrismaException,
    CustomAuthorizationException,
)


# Function that returns a fastapi instance after necessary modifications
def init(routes_list: list[APIRouter]):
    app = FastAPI(title="Art&Craft Eshop", version="0.0.1")
    # list comprehension. Includes all of our api routes in the main app
    [app.include_router(route) for route in routes_list]

    # add custom exception handlers
    @app.exception_handler(CustomGeneralException)
    def custom_general_exception_handler(request: Request, exc: CustomGeneralException):
        raise HTTPException(
            status_code=exc.status_code, detail=[{"msg": exc.error_msg}]
        )
    
    @app.exception_handler(CustomPrismaException)
    def custom_prisma_exception_handler(request: Request, exc: CustomPrismaException):
        raise HTTPException(status_code=exc.status_code, detail=[{"msg": exc.error_msg}])

    @app.exception_handler(CustomAuthorizationException)
    def custom_authorization_exception_handler(request:Request,exc: CustomAuthorizationException):
        raise HTTPException(
            status_code=exc.status_code, detail=[{"msg": exc.error_msg}]
        )

    return app


routes_list = [
    users.router,
    carts.router,
    orders.router,
    products.router,
    reviews.router,
    shops.router,
]


app = init(routes_list)




@app.get("/")
async def root():
    return "Welcome to the Arts&Crfat Eshop Homepage"


# Run "python main.py" in your terminal
# Or run the command "uvicorn main:app --reload"
# It should start running our api at "http://127.0.0.1:8000/docs" [Go to the link after running any one of the above commands]
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
