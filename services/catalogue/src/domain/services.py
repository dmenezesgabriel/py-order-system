import logging
from typing import Optional

from src.config import get_config
from src.domain.entities import Category, Product
from src.domain.enums import ProductEventType
from src.domain.events import ProductEvent
from src.domain.exceptions import (
    DeleteProductError,
    DuplicatedProduct,
    GetProductError,
    InvalidDescription,
    InvalidImageUrl,
    InvalidInventory,
    InvalidName,
    InvalidPrice,
    InvalidSku,
    OutdatedProduct,
    ProductAlreadyExist,
    ProductCreationError,
    ProductNotFound,
    UpdateProductError,
)
from src.domain.value_objects import Inventory, Price
from src.port import ProductEventPublisher, ProductRepository

config = get_config()
logger = logging.getLogger("app")


class CatalogueService:
    def __init__(
        self,
        product_repository: ProductRepository,
        product_event_publisher: ProductEventPublisher,
    ):
        self.__product_repository = product_repository
        self.__product_event_publisher = product_event_publisher

    def create_product(
        self,
        sku: str,
        name: str,
        description: str,
        price: Optional[Price] = None,
        inventory: Optional[Inventory] = None,
        category: Optional[Category] = None,
        image_url: Optional[str] = None,
    ) -> Product:
        try:
            product = Product(
                sku=sku,
                name=name,
                description=description,
                image_url=image_url,
                price=price,
                inventory=inventory,
                category=category,
            )
            created_product: Product = (
                self.__product_repository.create_product(
                    product=product,
                    on_duplicate_sku=ProductAlreadyExist(
                        "Product already exists"
                    ),
                    on_not_found=ProductNotFound(
                        "Product has not been created"
                    ),
                )
            )
            product_event = ProductEvent(
                type=ProductEventType.CREATED, product=product
            )
            self.__product_event_publisher.publish(product_event=product_event)
            return created_product
        except (
            InvalidSku,
            InvalidPrice,
            InvalidInventory,
            InvalidName,
            InvalidDescription,
            InvalidImageUrl,
            ProductAlreadyExist,
        ) as error:
            logger.error(error)
            raise
        except Exception as error:
            logger.error(error)
            raise ProductCreationError(f"Error creating product: {error}")

    def get_product_by_sku(self, sku: str) -> Product:
        try:
            Product.validate_sku(sku)
            product: Product = self.__product_repository.get_product_by_sku(
                sku=sku, on_not_found=ProductNotFound("Product not found")
            )
            if product is None:
                raise ProductNotFound("Product not found")
            return product
        except (InvalidSku, ProductNotFound) as error:
            logger.error(error)
            raise
        except Exception as error:
            logger.error(error)
            raise GetProductError(f"Error getting product: {error}")

    def update_product(
        self,
        sku: str,
        name: str,
        description: str,
        image_url: Optional[str] = None,
        price: Optional[Price] = None,
        inventory: Optional[Inventory] = None,
        category: Optional[Category] = None,
    ) -> Product:
        try:
            product = Product(
                sku=sku,
                name=name,
                description=description,
                image_url=image_url,
                price=price,
                inventory=inventory,
                category=category,
            )
            updated_product: Product = (
                self.__product_repository.update_product(
                    product=product,
                    on_not_found=ProductNotFound("Product not found"),
                    on_outdated_version=OutdatedProduct("Outdated version"),
                    on_duplicate=DuplicatedProduct("Duplicated product"),
                )
            )
            product_event = ProductEvent(
                type=ProductEventType.UPDATED, product=product
            )
            self.__product_event_publisher.publish(product_event=product_event)

            return updated_product
        except (
            DuplicatedProduct,
            InvalidSku,
            InvalidPrice,
            InvalidName,
            InvalidDescription,
            InvalidInventory,
            InvalidImageUrl,
            ProductNotFound,
        ) as error:
            logger.error(error)
            raise
        except Exception as error:
            logger.error(error)
            raise UpdateProductError(f"Error updating product {error}")

    def delete_product(self, sku: str) -> bool:
        try:
            Product.validate_sku(sku)
            self.__product_repository.delete_product(
                sku=sku, on_not_found=ProductNotFound("Product not found")
            )
            product_event = ProductEvent(
                type=ProductEventType.DELETED, sku=sku
            )
            self.__product_event_publisher.publish(product_event=product_event)

            return True
        except (InvalidSku, ProductNotFound) as error:
            logger.error(error)
            raise
        except Exception as error:
            logger.error(error)
            raise DeleteProductError(f"Error deleting product: {error}")
