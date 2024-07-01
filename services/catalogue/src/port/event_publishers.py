from abc import ABC, abstractmethod

from src.domain.entities.product import Product


class ProductEventPublisher(ABC):
    @abstractmethod
    def publish(self, product: Product) -> None:
        raise NotImplementedError
