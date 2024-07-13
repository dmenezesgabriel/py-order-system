from collections import namedtuple
from typing import NamedTuple, cast
from uuid import uuid4

from src.domain.entities import Category, Product
from src.domain.value_objects import Inventory, Price


class ProductHelper:
    @staticmethod
    def create_product() -> Product:
        return Product(
            id=None,
            sku="test_sku",
            name="Test Product",
            description="Test Description",
            image_url="http://example.com/image.png",
            price=Price(id=uuid4(), value=100.0, discount_percent=0.0),
            inventory=Inventory(id=uuid4(), quantity=10, reserved=0),
            category=Category(id=uuid4(), name="Test Category"),
        )

    @staticmethod
    def create_product_tuple(product: Product) -> NamedTuple:
        Row = namedtuple(
            "Row",
            [
                "product_id",
                "product_sku",
                "product_version",
                "product_name",
                "product_description",
                "product_image_url",
                "price_id",
                "price_value",
                "price_discount_percent",
                "inventory_id",
                "inventory_quantity",
                "inventory_reserved",
                "category_id",
                "category_name",
            ],
        )
        return Row(
            product.id,
            product.sku,
            1,
            product.name,
            product.description,
            product.image_url,
            cast(Price, product.price).id,
            cast(Price, product.price).value,
            cast(Price, product.price).discount_percent,
            cast(Inventory, product.inventory).id,
            cast(Inventory, product.inventory).quantity,
            cast(Inventory, product.inventory).reserved,
            cast(Category, product.category).id,
            cast(Category, product.category).name,
        )
