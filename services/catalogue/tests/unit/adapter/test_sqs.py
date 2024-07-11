import unittest
from unittest.mock import patch

from src.adapter.exceptions import SqsException
from src.adapter.sqs import SQSAdapter
from src.domain.enums import ProductEventType
from src.domain.events import ProductEvent


class TestSQSAdapter(unittest.TestCase):
    @patch("boto3.client")
    def setUp(self, mock_boto_client) -> None:
        self.queue_name = "test-queue"
        self.aws_access_key_id = "test-access-key"
        self.aws_secret_access_key = "test-secret-key"
        self.endpoint_url = "http://localhost:4566"
        self.region_name = "us-east-1"

        self.sqs_adapter = SQSAdapter(
            self.queue_name,
            self.aws_access_key_id,
            self.aws_secret_access_key,
            self.endpoint_url,
            self.region_name,
        )

        self.mock_sqs_client = mock_boto_client.return_value

    def test_should_get_queue_url(self) -> None:
        # Arrange
        self.mock_sqs_client.get_queue_url.return_value = {
            "QueueUrl": "http://test-queue-url"
        }

        # Act
        queue_url = self.sqs_adapter._SQSAdapter__get_queue_url()

        # Assert
        self.assertEqual(queue_url, "http://test-queue-url")
        self.mock_sqs_client.get_queue_url.assert_called_once_with(
            QueueName=self.queue_name
        )

    def test_get_queue_url_should_fail(self) -> None:
        # Arrange
        self.mock_sqs_client.get_queue_url.side_effect = Exception(
            "Queue not found"
        )

        # Act & Assert
        with self.assertRaises(SqsException) as context:
            self.sqs_adapter._SQSAdapter__get_queue_url()

        self.assertEqual(
            context.exception.args[0]["code"], "sqs.error.queue.unavailable"
        )
        self.assertIn("Queue not found", context.exception.args[0]["message"])

    @patch.object(
        ProductEvent,
        "to_json",
        return_value='{"type": "deleted", "sku": "123"}',
    )
    def test_should_publish_message(self, mock_to_json) -> None:
        # Arrange
        self.mock_sqs_client.get_queue_url.return_value = {
            "QueueUrl": "http://test-queue-url"
        }
        self.mock_sqs_client.send_message.return_value = {}

        #  Act
        product_event = ProductEvent(type=ProductEventType.DELETED, sku="123")
        self.sqs_adapter.publish(product_event)

        # Assert
        self.mock_sqs_client.get_queue_url.assert_called_once_with(
            QueueName=self.queue_name
        )
        self.mock_sqs_client.send_message.assert_called_once_with(
            QueueUrl="http://test-queue-url",
            MessageBody='{"type": "deleted", "sku": "123"}',
            DelaySeconds=1,
        )

    def test_publish_message_should_fail(self) -> None:
        # Arrange
        self.mock_sqs_client.get_queue_url.return_value = {
            "QueueUrl": "http://test-queue-url"
        }
        self.mock_sqs_client.send_message.side_effect = Exception(
            "Send message failed"
        )

        product_event = ProductEvent(type=ProductEventType.DELETED, sku="123")

        # Act & Assert
        with self.assertRaises(SqsException) as context:
            self.sqs_adapter.publish(product_event)

        self.assertEqual(
            context.exception.args[0]["code"], "sqs.error.queue.send_message"
        )
        self.assertIn(
            "Send message failed", context.exception.args[0]["message"]
        )


if __name__ == "__main__":
    unittest.main()
