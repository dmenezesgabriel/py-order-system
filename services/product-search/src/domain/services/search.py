import logging
from typing import List, Optional

from src.config import get_config
from src.domain.entities import Product
from src.domain.exceptions import (
    GetProductError,
    InvalidDescription,
    InvalidName,
    InvalidSku,
    ProductNotFound,
)
from src.port import ProductRepository

config = get_config()
logger = logging.getLogger("app")


class SearchService:
    def __init__(self, product_repository: ProductRepository):
        self.__product_repository = product_repository

    def find_by_sku(self, sku: str) -> Product:
        try:
            product: Product = self.__product_repository.find_product_by_sku(
                sku=sku,
                on_not_found=ProductNotFound(f"Product not found for: {sku}"),
            )
            if product is None:
                raise ProductNotFound("Product not found")
            return product
        except (InvalidSku, ProductNotFound) as error:
            logger.error(error)
            raise
        except Exception as error:
            logger.error("Error finding product: {error}")
            raise GetProductError(f"Error getting product: {error}")

    def find_by_params(
        self,
        sku: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        not_found_message = f"Product not found for sku: {sku} "
        not_found_message += f"name: {name}, description: {description}"
        try:
            products: List[Product] = (
                self.__product_repository.find_products_by_params(
                    sku=sku,
                    name=name,
                    description=description,
                    on_not_found=ProductNotFound(not_found_message),
                )
            )
            if products is None:
                raise ProductNotFound("Product not found")
            return products
        except (
            InvalidSku,
            InvalidDescription,
            InvalidName,
            ProductNotFound,
        ) as error:
            logger.error(error)
            raise
        except Exception as error:
            logger.error("Error finding product: {error}")
            raise GetProductError(f"Error getting product: {error}")
