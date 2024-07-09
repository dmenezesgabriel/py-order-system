from abc import ABC, abstractmethod

from src.domain.events import ProductEvent


class ProductEventPublisher(ABC):
    @abstractmethod
    def publish(self, product_event: ProductEvent) -> None:
        raise NotImplementedError
