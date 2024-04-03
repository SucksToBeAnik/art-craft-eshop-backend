import uvicorn
from fastapi import APIRouter, FastAPI

from routes import carts
from routes.auth import users
from routes.products import products
from routes.reviews import reviews
from routes.shops import shops


# Function that returns a fastapi instance after necessary modifications
def init(routes_list:list[APIRouter]):
    app = FastAPI(
        title="Art&Craft Eshop",
        version="0.0.1"
    )

    # list comprehension. Includes all of our api routes in the main app
    [app.include_router(route) for route in routes_list]

    return app

routes_list = [carts.router, products.router, reviews.router, shops.router, users.router]
app = init(routes_list)


@app.get('/')
async def root():
    return 'Welcome to the Arts&Crfat Eshop Homepage'


# Run "python main.py" in your terminal
# Or run the command "uvicorn main:app --reload"
# It should start running our api at "http://127.0.0.1:8000/docs" [Go to the link after running any one of the above commands]
if __name__ == '__main__':
    uvicorn.run("main:app",host="127.0.0.1",port=8000, reload=True)
