from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class InventoryDTO(BaseModel):
    quantity: int
    reserved: int


class PriceDTO(BaseModel):
    value: float
    discount_percent: float


class ProductRequestDTO(BaseModel):
    sku: str
    name: str
    description: str
    image_url: str
    price: PriceDTO
    inventory: InventoryDTO


class ProductResponseDTO(BaseModel):
    id: Optional[UUID]
    sku: str
    name: str
    description: str
    image_url: Optional[str]
    price: PriceDTO
    inventory: InventoryDTO
