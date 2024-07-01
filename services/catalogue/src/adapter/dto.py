from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class InventoryDTO(BaseModel):
    quantity: int
    reserved: Optional[int] = 0


class PriceDTO(BaseModel):
    value: float
    discount_percent: float


class ProductRequestDTO(BaseModel):
    sku: str
    name: str
    description: str
    image_url: Optional[str] = None
    price: Optional[PriceDTO] = None
    inventory: Optional[InventoryDTO] = None


class ProductResponseDTO(BaseModel):
    id: Optional[UUID]
    sku: str
    name: str
    description: str
    image_url: Optional[str] = None
    price: Optional[PriceDTO] = None
    inventory: Optional[InventoryDTO] = None
