from src.domain.entities import Product
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
        image_url: str,
        price: Price,
        inventory: Inventory,
    ) -> Product:
        try:
            product = Product(
                sku=sku,
                name=name,
                description=description,
                image_url=image_url,
                price=price,
                inventory=inventory,
            )
            created_product: Product = (
                self.__product_repository.create_product(
                    product=product,
                    on_duplicate_sku=ProductAlreadyExist(
                        "Product already exists"
                    ),
                )
            )
            self.__product_event_publisher.publish(product=product)
            return created_product
        except (
            InvalidSku,
            InvalidPrice,
            InvalidInventory,
            InvalidName,
            InvalidDescription,
            InvalidImageUrl,
            ProductAlreadyExist,
        ):
            raise
        except Exception as error:
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
        except (InvalidSku, ProductNotFound):
            raise
        except Exception as error:
            raise GetProductError(f"Error getting product: {error}")

    def update_product(
        self,
        sku: str,
        name: str,
        description: str,
        image_url: str,
        price: Price,
        inventory: Inventory,
    ) -> Product:
        try:
            product = Product(
                sku=sku,
                name=name,
                description=description,
                image_url=image_url,
                price=price,
                inventory=inventory,
            )
            updated_product: Product = (
                self.__product_repository.update_product(
                    product=product,
                    on_not_found=ProductNotFound("Product not found"),
                    on_outdated_version=OutdatedProduct("Outdated version"),
                    on_duplicate=DuplicatedProduct("Duplicated product"),
                )
            )
            self.__product_event_publisher.publish(product=product)
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
        ):
            raise

        except Exception as error:
            raise UpdateProductError(f"Error updating product {error}")

    def delete_product(self, sku: str) -> bool:
        try:
            Product.validate_sku(sku)
            self.__product_repository.delete_product(
                sku=sku, on_not_found=ProductNotFound("Product not found")
            )
            return True
        except (InvalidSku, ProductNotFound):
            raise
        except Exception as error:
            raise DeleteProductError(f"Error deleting product: {error}")
