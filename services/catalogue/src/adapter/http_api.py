import logging

from fastapi import APIRouter, HTTPException
from src.adapter.dto import (
    CategoryDTO,
    InventoryDTO,
    PriceDTO,
    ProductRequestDTO,
    ProductResponseDTO,
)
from src.config import get_config
from src.domain.entities import Category, Product
from src.domain.exceptions import (
    DuplicatedProduct,
    InvalidDescription,
    InvalidImageUrl,
    InvalidInventory,
    InvalidName,
    InvalidPrice,
    InvalidSku,
    OutdatedProduct,
    ProductAlreadyExist,
    ProductNotFound,
)
from src.domain.services import CatalogueService
from src.domain.value_objects import Inventory, Price

config = get_config()
logger = logging.getLogger("app")


class HTTPApiAdapter:
    def __init__(self, catalogue_service: CatalogueService) -> None:
        self.__catalogue_service = catalogue_service
        self.router = APIRouter()
        self.router.add_api_route(
            "/product", self.create_product, methods=["POST"]
        )
        self.router.add_api_route(
            "/product/{sku}", self.get_product_by_sku, methods=["GET"]
        )
        self.router.add_api_route(
            "/product/{sku}", self.update_product, methods=["PUT"]
        )
        self.router.add_api_route(
            "/product/{sku}", self.delete_product, methods=["DELETE"]
        )

    def create_product(self, product: ProductRequestDTO) -> ProductResponseDTO:
        try:
            inventory = None
            price = None
            category = None
            if product.inventory is not None:
                inventory = Inventory(
                    quantity=product.inventory.quantity,
                    reserved=product.inventory.reserved or 0,
                )
            if product.price is not None:
                price = Price(
                    value=product.price.value,
                    discount_percent=product.price.discount_percent,
                )

            if product.category is not None:
                category = Category(name=product.category.name)

            created_product: Product = self.__catalogue_service.create_product(
                sku=product.sku,
                name=product.name,
                description=product.description,
                image_url=product.image_url,
                price=price,
                inventory=inventory,
                category=category,
            )

            inventory_dto = None
            price_dto = None
            category_dto = None
            if created_product.price:
                price_dto = PriceDTO(
                    value=created_product.price.value,
                    discount_percent=created_product.price.discount_percent,
                )
            if created_product.inventory:
                inventory_dto = InventoryDTO(
                    quantity=created_product.inventory.quantity,
                    reserved=created_product.inventory.reserved,
                )
            if created_product.category:
                category_dto = CategoryDTO(name=created_product.category.name)

            return ProductResponseDTO(
                id=created_product.id,
                sku=created_product.sku,
                name=created_product.name,
                description=created_product.description,
                image_url=created_product.image_url,
                price=price_dto,
                inventory=inventory_dto,
                category=category_dto,
            )

        except (
            InvalidSku,
            InvalidDescription,
            InvalidImageUrl,
            InvalidInventory,
            InvalidName,
            InvalidPrice,
        ) as error:
            logger.error(error)
            raise HTTPException(
                status_code=400, detail=f"Error creating product {error}"
            )
        except (ProductAlreadyExist, DuplicatedProduct) as error:
            logger.error(error)
            raise HTTPException(
                status_code=409, detail=f"Error creating product {error}"
            )
        except Exception as error:
            logger.error(error)
            raise HTTPException(
                status_code=500, detail=f"Error creating product: {error}"
            )

    def get_product_by_sku(self, sku: str) -> ProductResponseDTO:
        try:
            product = self.__catalogue_service.get_product_by_sku(sku=sku)
            price = None
            inventory = None
            category = None
            if product.price:
                price = PriceDTO(
                    value=product.price.value,
                    discount_percent=product.price.discount_percent,
                )
            if product.inventory:
                inventory = InventoryDTO(
                    quantity=product.inventory.quantity,
                    reserved=product.inventory.reserved,
                )
            if product.category:
                category = CategoryDTO(name=product.category.name)
            return ProductResponseDTO(
                id=product.id,
                sku=product.sku,
                name=product.name,
                description=product.description,
                image_url=product.image_url,
                price=price,
                inventory=inventory,
                category=category,
            )
        except InvalidSku as error:
            logger.error(error)
            raise HTTPException(
                status_code=400, detail=f"Error getting product: {error}"
            )
        except ProductNotFound as error:
            logger.error(error)
            raise HTTPException(
                status_code=404, detail=f"Error getting product: {error}"
            )
        except Exception as error:
            logger.error(error)
            raise HTTPException(
                status_code=500, detail=f"Error getting product: {error}"
            )

    def update_product(
        self, sku: str, product: ProductRequestDTO
    ) -> ProductResponseDTO:
        try:
            inventory = None
            price = None
            category = None
            if product.inventory is not None:
                inventory = Inventory(
                    quantity=product.inventory.quantity,
                    reserved=product.inventory.reserved,
                )
            if product.price is not None:
                price = Price(
                    value=product.price.value,
                    discount_percent=product.price.discount_percent,
                )
            if product.category is not None:
                category = Category(name=product.category.name)
            updated_product: Product = self.__catalogue_service.update_product(
                sku=sku,
                name=product.name,
                description=product.description,
                image_url=product.image_url,
                price=price,
                inventory=inventory,
                category=category,
            )
            inventory_dto = None
            price_dto = None
            category_dto = None
            if updated_product.inventory:
                inventory_dto = InventoryDTO(
                    quantity=updated_product.inventory.quantity,
                    reserved=updated_product.inventory.reserved,
                )
            if updated_product.price:
                price_dto = PriceDTO(
                    value=updated_product.price.value,
                    discount_percent=updated_product.price.discount_percent,
                )
            if updated_product.category:
                category_dto = CategoryDTO(name=updated_product.category.name)
            return ProductResponseDTO(
                id=updated_product.id,
                name=updated_product.name,
                description=updated_product.description,
                image_url=updated_product.image_url,
                inventory=inventory_dto,
                price=price_dto,
                category=category_dto,
                sku=updated_product.sku,
            )
        except (
            InvalidSku,
            InvalidPrice,
            InvalidName,
            InvalidInventory,
            InvalidPrice,
            InvalidImageUrl,
            InvalidDescription,
        ) as error:
            logger.error(error)
            raise HTTPException(
                status_code=400, detail=f"Error updating product: {error}"
            )
        except ProductNotFound as error:
            logger.error(error)
            raise HTTPException(
                status_code=404, detail=f"Error updating product: {error}"
            )
        except OutdatedProduct as error:
            logger.error(error)
            raise HTTPException(
                status_code=409, detail=f"Error updating product: {error}"
            )
        except Exception as error:
            logger.error(error)
            raise HTTPException(
                status_code=500, detail=f"Error updating product: {error}"
            )

    def delete_product(self, sku: str) -> bool:
        try:
            self.__catalogue_service.delete_product(sku)
            return True
        except InvalidSku as error:
            logger.error(error)
            raise HTTPException(
                status_code=400, detail=f"Error deleting product: {error}"
            )
        except ProductNotFound as error:
            logger.error(error)
            raise HTTPException(
                status_code=404, detail=f"Error deleting product: {error}"
            )
        except Exception as error:
            logger.error(error)
            raise HTTPException(
                status_code=500, detail=f"Error deleting product: {error}"
            )
