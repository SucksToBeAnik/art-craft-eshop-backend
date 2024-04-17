from pydantic import BaseModel, Field
from typing import Annotated, Optional, Literal

ProductType = Literal["ARTWORK","SCULPTURE","OTHER"]


class CreateProduct(BaseModel):
    name: Annotated[str, Field(min_length=3)]
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    images: list[str]
    price: Annotated[int, Field(gt=0)]
    available: bool = True
    discount: Optional[int] = None

    product_type: ProductType
    owner_shop_id: str
    # customer_id: Optional[str] = None
    # owner_cart_id: Optional[str] = None