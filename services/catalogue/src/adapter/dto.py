from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class InventoryDTO(BaseModel):
    quantity: int
    reserved: Optional[int] = 0


class PriceDTO(BaseModel):
    value: float
    discount_percent: float


class CategoryDTO(BaseModel):
    name: str


class ProductRequestDTO(BaseModel):
    sku: str
    name: str
    description: str
    image_url: Optional[str] = None
    price: Optional[PriceDTO] = None
    inventory: Optional[InventoryDTO] = None
    category: Optional[CategoryDTO] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "sku": "00056789",
                    "name": "ear phones",
                    "description": "something to put on your ears",
                    "image_url": "http://example.com",
                    "price": {"value": 10.0, "discount_percent": 0},
                    "inventory": {"quantity": 10, "reserved": 0},
                    "category": {"name": "electronics"},
                }
            ]
        }
    }


class ProductResponseDTO(BaseModel):
    id: Optional[UUID]
    sku: str
    name: str
    description: str
    image_url: Optional[str] = None
    price: Optional[PriceDTO] = None
    inventory: Optional[InventoryDTO] = None
    category: Optional[CategoryDTO] = None
