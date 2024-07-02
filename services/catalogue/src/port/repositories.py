from abc import ABC, abstractmethod

from src.domain.entities.product import Product


class ProductRepository(ABC):
    @abstractmethod
    def create_product(
        self,
        product: Product,
        on_duplicate_sku: Exception,
        on_not_found: Exception,
    ) -> Product:
        raise NotImplementedError

    @abstractmethod
    def get_product_by_sku(self, sku: str, on_not_found: Exception) -> Product:
        raise NotImplementedError

    @abstractmethod
    def update_product(
        self,
        product: Product,
        on_not_found: Exception,
        on_outdated_version: Exception,
        on_duplicate: Exception,
    ) -> Product:
        raise NotImplementedError

    @abstractmethod
    def delete_product(self, sku, on_not_found: Exception) -> bool:
        raise NotImplementedError
