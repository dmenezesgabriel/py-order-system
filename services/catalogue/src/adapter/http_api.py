from adapter.dto import (
    InventoryDTO,
    PriceDTO,
    ProductRequestDTO,
    ProductResponseDTO,
)
from domain.entities import Product
from domain.exceptions import (
    DuplicatedProduct,
    InvalidDescription,
    InvalidImageUrl,
    InvalidInventory,
    InvalidName,
    InvalidPrice,
    InvalidSku,
    ProductAlreadyExist,
    ProductNotFound,
)
from domain.services import CatalogueService
from domain.value_objects import Inventory, Price
from fastapi import APIRouter, HTTPException


class HTTPAPIAdapter:
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
            created_product: Product = self.__catalogue_service.create_product(
                sku=product.sku,
                name=product.name,
                description=product.description,
                image_url=product.image_url,
                price=product.price,
                inventory=product.inventory,
            )
            price = PriceDTO(
                value=created_product.price.value,
                discount_percent=created_product.price.discount_percent,
            )
            inventory = InventoryDTO(
                quantity=created_product.inventory.quantity,
                reserved=created_product.inventory.reserved,
            )
            return ProductResponseDTO(
                id=created_product.id,
                sku=created_product.sku,
                name=created_product.name,
                description=created_product.description,
                image_url=created_product.image_url,
                price=price,
                inventory=inventory,
            )
        except (
            InvalidSku,
            InvalidDescription,
            InvalidImageUrl,
            InvalidInventory,
            InvalidName,
            InvalidPrice,
        ) as error:
            raise HTTPException(
                status_code=400, detail=f"Error creating product {error}"
            )
        except (ProductAlreadyExist, DuplicatedProduct) as error:
            raise HTTPException(
                status_code=409, detail=f"Error creating product {error}"
            )
        except Exception as error:
            raise HTTPException(
                status_code=500, detail=f"Error creating product: {error}"
            )

    def get_product_by_sku(self, sku: str) -> ProductResponseDTO:
        try:
            product = self.__catalogue_service.get_product_by_sku(sku=sku)
            price = PriceDTO(
                value=product.price.value,
                discount_percent=product.price.discount_percent,
            )
            inventory = InventoryDTO(
                quantity=product.inventory.quantity,
                reserved=product.inventory.reserved,
            )
            return ProductResponseDTO(
                id=product.id,
                sku=product.sku,
                name=product.name,
                description=product.description,
                image_url=product.image_url,
                price=price,
                inventory=inventory,
            )
        except InvalidSku as error:
            raise HTTPException(
                status_code=400, detail=f"Error getting product: {error}"
            )
        except ProductNotFound as error:
            raise HTTPException(
                status_code=404, detail=f"Error getting product: {error}"
            )
        except Exception as error:
            raise HTTPException(
                status_code=500, detail=f"Error getting product: {error}"
            )

    def update_product(self, sku: str, product: ProductRequestDTO):
        try:
            inventory = Inventory(
                quantity=product.inventory.quantity,
                reserved=product.inventory.reserved,
            )
            price = Price(
                value=product.price.value,
                discount_percent=product.price.discount_percent,
            )
            updated_product: Product = self.__catalogue_service.update_product(
                sku=sku,
                name=product.name,
                description=product.description,
                image_url=product.image_url,
                price=price,
                inventory=inventory,
            )
            inventory_dto = InventoryDTO(
                quantity=updated_product.inventory.quantity,
                reserved=updated_product.inventory.reserved,
            )

            price_dto = PriceDTO(
                value=updated_product.price.value,
                discount_percent=updated_product.price.discount_percent,
            )
            return ProductResponseDTO(
                id=updated_product.id,
                name=updated_product.name,
                description=updated_product.description,
                image_url=updated_product.image_url,
                inventory=inventory_dto,
                price=price_dto,
                sku=updated_product.sku,
            )
        except Exception as error:
            pass
