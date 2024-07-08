from abc import ABC, abstractmethod


class ProductEventListener(ABC):
    @abstractmethod
    def receive_message(self):
        raise NotImplementedError

    @abstractmethod
    def delete_message(self, receipt_handle: str):
        raise NotImplementedError
