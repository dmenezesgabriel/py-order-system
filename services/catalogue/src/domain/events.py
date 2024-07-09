import json
from typing import Optional

from src.domain.entities import Product
from src.domain.enums import ProductEventType


class ProductEvent:

    def __init__(
        self,
        type: ProductEventType,
        product: Optional[Product] = None,
        sku: Optional[str] = None,
    ) -> None:
        self._type = type
        self._product = product
        self._sku = sku

        self.validade_event()

    def validade_event(self):
        if self.type == ProductEventType.CREATED and self.product is None:
            raise Exception("CREATED product event must have valid product")
        if self.type == ProductEventType.UPDATED and self.product is None:
            raise Exception("UPDATED product event must have valid product")
        if self.type == ProductEventType.DELETED and self.sku is None:
            raise Exception("DELETED product event must have valid sku")

    @property
    def type(self) -> ProductEventType:
        return self._type

    @property
    def sku(self) -> Optional[str]:
        return self._sku

    @property
    def product(self) -> Optional[Product]:
        return self._product

    def to_dict(self):
        product = None
        sku = None
        if self.product is not None:
            product = self.product.to_dict()
        if self.sku is not None:
            sku = self.sku

        return {"type": self.type.string, "product": product, "sku": sku}

    def to_json(self):
        return json.dumps(self.to_dict())
