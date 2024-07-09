from enum import Enum


class ProductEventType(Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"

    @property
    def string(self):
        return self.value
