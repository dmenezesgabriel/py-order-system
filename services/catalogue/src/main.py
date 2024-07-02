import os

from fastapi import FastAPI
from src.adapter.http_api import HTTPAPIAdapter
from src.adapter.postgres import ProductPostgresAdapter
from src.adapter.sqs import SQSAdapter
from src.domain.services import CatalogueService

DATABASE_URL = os.getenv("DATABASE_URL")
QUEUE_NAME = "product-update"
ENDPOINT_URL = "http://localstack:4566"
REGION_NAME = "us-east-1"
AWS_ACCESS_KEY_ID = "LKIAQAAAAAAAFFCVQQVU"
AWS_SECRET_ACCESS_KEY = "wEWEKcBy8wQDOp5STKPfUUS/wykE6er26Taj/YFP"

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    product_postgres_adapter = ProductPostgresAdapter(
        database_url=DATABASE_URL
    )
    sqs_adapter = SQSAdapter(
        queue_name=QUEUE_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        endpoint_url=ENDPOINT_URL,
        region_name=REGION_NAME,
    )
    catalogue_service = CatalogueService(
        product_event_publisher=sqs_adapter,
        product_repository=product_postgres_adapter,
    )
    http_api_adapter = HTTPAPIAdapter(catalogue_service=catalogue_service)
    app.include_router(http_api_adapter.router)
