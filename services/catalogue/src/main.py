from adapter.http_api import HTTPAPIAdapter
from adapter.mysql import ProductMySQLAdapter
from adapter.sqs import SQSAdapter
from domain.services import CatalogueService
from fastapi import FastAPI

DATABASE_URL = (
    "mysql+mysqlconnector://catalogue_user:password@db-services:3306/catalogue"
)
QUEUE_NAME = "product-update"
ENDPOINT_URL = "http://localstack:4566"
REGION_NAME = "us-east-1"
AWS_ACCESS_KEY_ID = "LKIAQAAAAAAAFFCVQQVU"
AWS_SECRET_ACCESS_KEY = "wEWEKcBy8wQDOp5STKPfUUS/wykE6er26Taj/YFP"

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    product_mysql_adapter = ProductMySQLAdapter(database_url=DATABASE_URL)
    sqs_adapter = SQSAdapter(
        queue_name=QUEUE_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        endpoint_url=ENDPOINT_URL,
        region_name=REGION_NAME,
    )
    catalogue_service = CatalogueService(
        product_event_publisher=sqs_adapter,
        product_repository=product_mysql_adapter,
    )
    http_api_adapter = HTTPAPIAdapter(catalogue_service=catalogue_service)
    app.include_router(http_api_adapter.router)
