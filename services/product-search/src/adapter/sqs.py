import boto3
from src.adapter.exceptions import SqsException
from src.port.event_listener import ProductEventListener


class SQSAdapter(ProductEventListener):
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

    def receive_message(self):
        queue_url = self.__get_queue_url()
        try:
            response = self.sqs.receive_message(
                QueueUrl=queue_url, MaxNumberOfMessages=10
            )
            return response.get("Messages", [])
        except Exception as error:
            raise SqsException(
                {
                    "code": "sqs.error.queue.receive_message",
                    "message": f"Error receiving message from queue: {error}",
                }
            )

    def delete_message(self, receipt_handle: str):
        queue_url = self.__get_queue_url()
        try:
            self.sqs.delete_message(
                QueueUrl=queue_url, ReceiptHandle=receipt_handle
            )
        except Exception as error:
            raise SqsException(
                {
                    "code": "sqs.error.queue.delete_message",
                    "message": f"Error deleting message from queue: {error}",
                }
            )
