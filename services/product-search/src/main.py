import json
import logging
import threading
import time
from typing import Any, Dict, List, Optional, Union

import boto3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from src.config import get_config

config = get_config()
logger = logging.getLogger("app")

app = FastAPI()

client = MongoClient(config.MONGO_URL)
db = client.busca_produto
produto_collection = db.produto


class Price(BaseModel):
    value: float
    discount_percent: float


class Inventory(BaseModel):
    quantity: int
    reserved: Optional[int] = 0


class Category(BaseModel):
    name: str


class Product(BaseModel):
    sku: str
    name: str
    description: str
    image_url: str
    price: Optional[Price] = None
    inventory: Optional[Inventory] = None
    category: Optional[Category] = None


sqs = boto3.client(
    "sqs",
    endpoint_url=config.ENDPOINT_URL,
    region_name=config.REGION_NAME,
    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
)
queues = {
    "product-update": "http://localstack:4566/000000000000/product-update",
}


def handle_sqs_message(queue_name: str, queue_url: str) -> None:
    while True:
        try:
            messages = sqs.receive_message(
                QueueUrl=queue_url, MaxNumberOfMessages=10
            )

            if "Messages" in messages:
                for message in messages["Messages"]:
                    process_message(message, queue_name)
                    sqs.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=message["ReceiptHandle"],
                    )

            time.sleep(5)

        except Exception as e:
            print(f"Error processing message for queue {queue_name}: {str(e)}")
            time.sleep(10)


def process_message(
    message: Dict[str, Union[str, Dict[str, Any]]], queue_name: str
) -> None:
    try:
        data = json.loads(message["Body"])
        logger.info(data)
        if queue_name == "product-update":
            event_type = data.get("type")
            if event_type in ["created", "updated"]:
                product_data = data.get("product")
                product = Product(**product_data)
                produto_collection.update_one(
                    {"sku": product.sku},
                    {
                        "$set": {
                            "name": product.name,
                            "description": product.description,
                            "image_url": product.image_url,
                            "price": {
                                "value": product.price.value,
                                "discount_percent": product.price.discount_percent,
                            },
                            "inventory": {
                                "quantity": product.inventory.quantity,
                                "reserved": product.inventory.reserved,
                            },
                            "category": {"name": product.category.name},
                        }
                    },
                    upsert=True,
                )
            if event_type == "deleted":
                sku_data = data.get("sku")
                produto_collection.delete_one({"sku": sku_data})
    except Exception as error:
        logger.error(error)
        raise


@app.get("/product/{sku}")
def get_product_by_sku(sku: str):
    try:
        result = produto_collection.find_one({"sku": sku})
        if result is None:
            raise HTTPException(
                status_code=404, detail="Produto não encontrado"
            )
        return Product(**result)
    except Exception as error:
        logger.error(error)
        raise HTTPException(status_code=500, detail="Erro ao buscar produto")


@app.get("/product")
def get_product_by_params(
    sku: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> List[Product]:
    query: Dict[str, Union[str, Dict[str, Any]]] = {}
    if sku:
        query["sku"] = sku
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    if description:
        query["description"] = {"$regex": description, "$options": "i"}

    try:
        result = list(produto_collection.find(query))
        if not result:
            raise HTTPException(
                status_code=204, detail="Produtos não encontrados na busca"
            )
        return [Product(**prod) for prod in result]
    except Exception as error:
        logger.error(error)
        raise HTTPException(status_code=500, detail="Erro ao buscar produtos")


@app.on_event("startup")
def start_sqs_handlers():
    logger.info("started event handler")
    for queue_name, queue_url in queues.items():
        threading.Thread(
            target=handle_sqs_message, args=(queue_name, queue_url)
        ).start()
