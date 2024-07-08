import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from src.adapter.dto import (
    CategoryDTO,
    InventoryDTO,
    PriceDTO,
    ProductResponseDTO,
)
from src.config import get_config
from src.domain.exceptions import (
    InvalidDescription,
    InvalidName,
    InvalidSku,
    ProductNotFound,
)
from src.domain.services import SearchService

config = get_config()
logger = logging.getLogger("app")


class HTTPAPIAdapter:
    def __init__(self, search_service: SearchService) -> None:
        self.__search_service = search_service
        self.router = APIRouter()
        self.router.add_api_route(
            "/product/{sku}", self.get_product_by_sku, methods=["GET"]
        )
        self.router.add_api_route(
            "/product", self.get_product_by_params, methods=["GET"]
        )

    def get_product_by_sku(self, sku: str) -> ProductResponseDTO:
        try:
            product = self.__search_service.find_by_sku(sku=sku)
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

    def get_product_by_params(
        self,
        sku: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        try:
            product = self.__search_service.find_by_params(
                sku=sku, name=name, description=description
            )
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
        except (InvalidSku, InvalidName, InvalidDescription) as error:
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
