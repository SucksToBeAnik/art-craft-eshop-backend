from pydantic import BaseModel, Field
from typing import Annotated, Optional

class Shop(BaseModel):
    name: Annotated[str, Field(min_length=3)]
    description: Annotated[Optional[str], Field(min_length=20)] = None
    location: Optional[str] = None
    website: Optional[str] = None
    owner_id: Optional[str] = None

class UpdateShop(BaseModel):
    name: Annotated[Optional[str], Field(min_length=3)] = None
    description: Annotated[Optional[str], Field(min_length=20)] = None
    location: Optional[str] = None
    website: Optional[str] = None
    

