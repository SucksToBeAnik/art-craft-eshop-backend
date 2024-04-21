from pydantic import BaseModel, Field
from typing import Annotated, Optional, Literal

ProductType = Literal["ARTWORK","SCULPTURE","OTHER"]



class Product(BaseModel):
    name: Annotated[str, Field(min_length=3)]
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    images: list[str] = []
    price: Annotated[int, Field(gt=0)]
    discount: Optional[int] = None
    product_type: ProductType



class CreateProduct(Product):
    owner_shop_id: str


class UpdateProduct(Product):
    name: Annotated[Optional[str], Field(min_length=3)] = None
    price: Annotated[Optional[int], Field(gt=0)] = None
    product_type: Optional[ProductType] = None
    available: Optional[bool] = None

