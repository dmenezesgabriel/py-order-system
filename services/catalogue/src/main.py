from fastapi import FastAPI
from src.adapter.http_api import HTTPApiAdapter
from src.adapter.postgres import ProductPostgresAdapter
from src.adapter.sqs import SQSAdapter
from src.config import get_config
from src.domain.services import CatalogueService

config = get_config()

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    product_postgres_adapter = ProductPostgresAdapter(
        database_url=config.DATABASE_URL
    )
    sqs_adapter = SQSAdapter(
        queue_name=config.QUEUE_NAME,
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        endpoint_url=config.ENDPOINT_URL,
        region_name=config.REGION_NAME,
    )
    catalogue_service = CatalogueService(
        product_event_publisher=sqs_adapter,
        product_repository=product_postgres_adapter,
    )
    http_api_adapter = HTTPApiAdapter(catalogue_service=catalogue_service)
    app.include_router(http_api_adapter.router)
