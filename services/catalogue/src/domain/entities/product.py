from typing import Optional
from uuid import UUID, uuid4

from src.domain.entities import Category
from src.domain.exceptions import (
    InvalidDescription,
    InvalidImageUrl,
    InvalidName,
    InvalidSku,
)
from src.domain.value_objects import Inventory, Price


class Product:

    def __init__(
        self,
        name: str,
        description: str,
        sku: str,
        image_url: Optional[str] = None,
        price: Optional[Price] = None,
        inventory: Optional[Inventory] = None,
        category: Optional[Category] = None,
        version: Optional[int] = None,
        id: Optional[UUID] = None,
        **kwargs
    ) -> None:

        self._id = id or uuid4()
        self._version = version
        self._sku = self.validate_sku(sku)
        self._name = self.validate_name(name)
        self._description = self.validate_description(description)
        self._image_url = self.validate_image_url(image_url)
        self._price = price
        self._inventory = inventory
        self._category = category

    @staticmethod
    def validate_sku(sku: str) -> str:
        if sku is None or sku == "":
            raise InvalidSku("Sku field is mandatory")
        if len(sku) < 3:
            raise InvalidSku("Sku can not have less than 3 characters.")
        return sku

    @staticmethod
    def validate_name(name: str) -> str:
        if name is None or name == "":
            raise InvalidName("Name field is mandatory.")
        if len(name) < 3:
            raise InvalidName("Name can not have less than 3 characters.")
        return name

    @staticmethod
    def validate_description(description: str) -> str:
        if description is None or description == "":
            raise InvalidDescription("Description field is mandatory.")
        if len(description) < 3:
            raise InvalidDescription(
                "Description can not have less than 3 characters."
            )
        return description

    @staticmethod
    def validate_image_url(image_url: Optional[str]) -> Optional[str]:
        if not image_url:
            return None
        if not image_url.startswith("http://") and not image_url.startswith(
            "https://"
        ):
            raise InvalidImageUrl("Image Url is invalid.")
        return image_url

    @property
    def id(self) -> Optional[UUID]:
        return self._id

    @property
    def version(self) -> Optional[int]:
        return self._version

    @property
    def sku(self) -> str:
        return self._sku

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def image_url(self) -> Optional[str]:
        return self._image_url

    @property
    def price(self) -> Optional[Price]:
        return self._price

    @property
    def inventory(self) -> Optional[Inventory]:
        return self._inventory

    @property
    def category(self) -> Optional[Category]:
        return self._category

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "version": self.version,
            "sku": self.sku,
            "name": self.name,
            "description": self.description,
            "image_url": self.image_url,
            "price": self.price.to_dict() if self.price else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
            "category": self.category.to_dict() if self.category else None,
        }
