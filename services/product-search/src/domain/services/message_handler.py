import time
from typing import Any, Dict

from src.domain.entities import Product
from src.port.event_listener import ProductEventListener
from src.port.repositories import ProductRepository


class MessageHandlerService:
    def __init__(
        self,
        event_listener: ProductEventListener,
        product_repository: ProductRepository,
    ):
        self.__event_listener = event_listener
        self.__product_repository = product_repository

    def handle_messages(self):
        while True:
            try:
                messages = self.__event_listener.receive_message()

                for message in messages:
                    self.process_message(message)
                    self.__event_listener.delete_message(
                        message["ReceiptHandle"]
                    )

                time.sleep(5)

            except Exception as e:
                print(f"Error processing message: {str(e)}")
                time.sleep(10)

    def process_message(self, message: Dict[str, Any]):
        data = message["Body"]
        try:
            product = Product(
                sku=data.get("sku"),
                name=data.get("name"),
            )
            self.__product_repository.save_or_update(product=product)

        except Exception as e:
            print(f"Error processing message: {str(e)}")
