from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities import Product


class ProductRepository(ABC):
    @abstractmethod
    def save_or_update(self, data: Product) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_product_by_sku(
        self, sku: str, on_not_found: Exception
    ) -> Product:
        raise NotImplementedError

    @abstractmethod
    def find_products_by_params(
        self,
        on_not_found: Exception,
        sku: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> List[Product]:
        raise NotImplementedError
