from fastapi import FastAPI
from pymongo import MongoClient
from src.adapter.http_api import HTTPAPIAdapter
from src.adapter.mongo import ProductMongoAdapter
from src.adapter.sqs import SQSAdapter
from src.config import get_config
from src.domain.services import MessageHandler, SearchService

config = get_config()

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    client = MongoClient(config.DATABASE_URL)
    product_mongo_adapter = ProductMongoAdapter(
        client=client,
        db_name="product-search",
        collection_name="product-collection",
    )
    sqs_adapter = SQSAdapter(
        queue_name=config.QUEUE_NAME,
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        endpoint_url=config.ENDPOINT_URL,
        region_name=config.REGION_NAME,
    )
    catalogue_service = SearchService(
        product_repository=product_mongo_adapter,
    )
    http_api_adapter = HTTPAPIAdapter(catalogue_service=catalogue_service)
    app.include_router(http_api_adapter.router)
