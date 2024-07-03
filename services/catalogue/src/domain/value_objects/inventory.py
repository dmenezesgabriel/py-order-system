from typing import Optional
from uuid import UUID, uuid4

from src.domain.exceptions import InvalidInventory


class Inventory:
    def __init__(
        self,
        quantity: int,
        reserved: Optional[int] = 0,
        id: Optional[UUID] = None,
    ) -> None:
        self._id = id or uuid4()
        self._quantity = self._validate_quantity(quantity)
        self._reserved = self._validate_reserved(reserved, quantity)

    @staticmethod
    def _validate_quantity(quantity: int) -> int:
        if quantity is None:
            raise InvalidInventory("Quantity field is mandatory.")
        if quantity < 0:
            raise InvalidInventory("Quantity can not be negative.")
        return quantity

    @staticmethod
    def _validate_reserved(reserved: Optional[int], quantity: int) -> int:
        if reserved is None:
            raise InvalidInventory("Reserved field is mandatory.")
        if reserved < 0:
            raise InvalidInventory("Reserved can not be negative.")
        if reserved > quantity:
            raise InvalidInventory("Reserved can not be higher than quantity.")
        return reserved

    @property
    def id(self) -> Optional[UUID]:
        return self._id

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def reserved(self) -> int:
        return self._reserved

    @property
    def in_stock(self) -> int:
        return self._quantity - self.reserved

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "quantity": self.quantity,
            "reserved": self.reserved,
            "in_stock": self.in_stock,
        }
