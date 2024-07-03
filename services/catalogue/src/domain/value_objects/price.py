from typing import Optional
from uuid import UUID, uuid4

from src.domain.exceptions import InvalidPrice


class Price:
    def __init__(
        self,
        value: float,
        discount_percent: float = 0,
        id: Optional[UUID] = None,
    ) -> None:
        self._id = id or uuid4()
        self._value = self._validate_price(value)
        self._discount_percent = self._validate_discount(discount_percent)

    @staticmethod
    def _validate_price(price_value: float) -> float:
        if price_value is None:
            raise InvalidPrice("Price value is a mandatory field.")
        if price_value < 0:
            raise InvalidPrice("Price value can not be negative.")
        return price_value

    @staticmethod
    def _validate_discount(discount_percent: float) -> float:
        if discount_percent is None:
            raise InvalidPrice("Discount value is a mandatory field.")
        if discount_percent < 0:
            raise InvalidPrice("Discount value can not be negative.")
        if discount_percent > 1:
            raise InvalidPrice("Discount value can not be higher than 100%.")
        return discount_percent

    @property
    def id(self) -> Optional[UUID]:
        return self._id

    @property
    def value(self) -> float:
        return self._value

    @property
    def discount_percent(self) -> float:
        return self._discount_percent

    @property
    def discounted_price(self) -> float:
        return self._value - self._value * self._discount_percent

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "value": self.value,
            "discount_percent": self.discount_percent,
            "discounted_price": self.discounted_price,
        }
