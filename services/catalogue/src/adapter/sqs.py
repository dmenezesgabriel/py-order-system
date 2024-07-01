import json

import boto3
from src.adapter.exceptions import SqsException
from src.domain.entities import Product
from src.port.event_publishers import ProductEventPublisher


class SQSAdapter(ProductEventPublisher):
    def __init__(
        self,
        queue_name: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        endpoint_url: str,
        region_name: str,
    ):
        self.__queue_name = queue_name
        self.__sqs = boto3.client(
            "sqs",
            endpoint_url=endpoint_url,
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

    def __get_queue_url(self) -> str:
        try:
            response = self.__sqs.get_queue_url(QueueName=self.__queue_name)
            return response.get("QueueUrl")
        except Exception as error:
            raise SqsException(
                {
                    "code": "sqs.error.queue.unavailable",
                    "message": f"Sqs Queue not found {error}",
                }
            )

    def publish(self, product: Product) -> None:
        queue_url = self.__get_queue_url()
        try:
            product_dict = product.to_dict()
            product_json = json.dumps(product_dict)
            self.__sqs.send_message(
                QueueUrl=queue_url, MessageBody=product_json
            )
        except Exception as error:
            raise SqsException(
                {
                    "code": "sqs.error.queue.send_message",
                    "message": f"Error sending message to sqs queue: {error}",
                }
            )
