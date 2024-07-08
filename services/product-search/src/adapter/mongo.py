import logging
from typing import Dict, List, Optional, Union

from pymongo import MongoClient
from src.config import get_config
from src.domain.entities import Product
from src.domain.value_objects import Category, Inventory, Price
from src.port.repositories import ProductRepository

config = get_config
logger = logging.getLogger("app")


class ProductMongoAdapter(ProductRepository):
    def __init__(
        self, client: MongoClient, db_name: str, collection_name: str
    ):
        self.collection = client[db_name][collection_name]

    def save_or_update(self, product: Product) -> None:
        self.collection.update_one(
            {"sku": product.sku},
            {
                "$set": {
                    "name": product.name,
                    "description": product.description,
                    "image_url": product.image_url,
                    "category": {"name": product.category.name},
                    "price": {
                        "value": product.price.value,
                        "discount_percent": product.price.discount_percent,
                    },
                    "inventory": {
                        "quantity": 10,
                        "reserved": 0,
                    },
                }
            },
            upsert=True,
        )

    def find_by_sku(self, sku: str, on_not_found: Exception) -> Product:
        try:
            result = self.collection.find_one({"sku": sku})
            if result is None:
                logger.error(f"Product not found for sku: {sku}")
                raise on_not_found
            price = Price(**result["price"])
            inventory = Inventory(**result["inventory"])
            category = Category(**result["category"])
            product = Product(
                **result, price=price, inventory=inventory, category=category
            )
            return product
        except Exception as error:
            logger.error(error)
            raise

    def find_by_params(
        self,
        on_not_found: Exception,
        sku: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> List[Product]:
        filter_dict: Dict[str, Union[str, Dict[str, str]]] = {}
        if sku:
            filter_dict["sku"] = sku
        if name:
            filter_dict["nome"] = {"$regex": f".*{name}.*", "$options": "i"}
        if description:
            filter_dict["descr"] = {
                "$regex": f".*{description}.*",
                "$options": "i",
            }
        try:
            result = self.collection.find(filter_dict)
            if result is None:
                raise on_not_found
            products: List[Product] = []
            for item in result:
                price = Price(**item["price"])
                inventory = Inventory(**item["inventory"])
                category = Category(**item["category"])
                product = Product(
                    **item,
                    price=price,
                    inventory=inventory,
                    category=category,
                )
                products.append(product)
            return products
        except Exception as error:
            logger.error(error)
            raise
