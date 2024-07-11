import unittest
from uuid import UUID, uuid4

from pydantic import ValidationError
from src.adapter.dto import (
    CategoryDTO,
    InventoryDTO,
    PriceDTO,
    ProductRequestDTO,
    ProductResponseDTO,
)


class TestDTOs(unittest.TestCase):
    def test_inventory_dto(self):
        # Arrange
        inventory = InventoryDTO(quantity=10, reserved=5)
        # Assert
        self.assertEqual(inventory.quantity, 10)
        self.assertEqual(inventory.reserved, 5)

    def test_price_dto(self):
        # Arrange
        price = PriceDTO(value=99.99, discount_percent=10.0)
        # Assert
        self.assertEqual(price.value, 99.99)
        self.assertEqual(price.discount_percent, 10.0)

    def test_category_dto(self):
        # Arrange
        category = CategoryDTO(name="electronics")
        # Assert
        self.assertEqual(category.name, "electronics")

    def test_product_request_dto(self):
        # Arrange
        product_request = ProductRequestDTO(
            sku="00056789",
            name="ear phones",
            description="something to put on your ears",
            image_url="http://example.com",
            price=PriceDTO(value=10.0, discount_percent=0),
            inventory=InventoryDTO(quantity=10, reserved=0),
            category=CategoryDTO(name="electronics"),
        )
        # Assert
        self.assertEqual(product_request.sku, "00056789")
        self.assertEqual(product_request.name, "ear phones")
        self.assertEqual(
            product_request.description, "something to put on your ears"
        )
        self.assertEqual(product_request.image_url, "http://example.com")
        self.assertEqual(product_request.price.value, 10.0)
        self.assertEqual(product_request.price.discount_percent, 0)
        self.assertEqual(product_request.inventory.quantity, 10)
        self.assertEqual(product_request.inventory.reserved, 0)
        self.assertEqual(product_request.category.name, "electronics")

    def test_product_response_dto(self):
        # Arrange
        product_response = ProductResponseDTO(
            id=uuid4(),
            sku="00056789",
            name="ear phones",
            description="something to put on your ears",
            image_url="http://example.com",
            price=PriceDTO(value=10.0, discount_percent=0),
            inventory=InventoryDTO(quantity=10, reserved=0),
            category=CategoryDTO(name="electronics"),
        )
        # Assert
        self.assertIsInstance(product_response.id, UUID)
        self.assertEqual(product_response.sku, "00056789")
        self.assertEqual(product_response.name, "ear phones")
        self.assertEqual(
            product_response.description, "something to put on your ears"
        )
        self.assertEqual(product_response.image_url, "http://example.com")
        self.assertEqual(product_response.price.value, 10.0)
        self.assertEqual(product_response.price.discount_percent, 0)
        self.assertEqual(product_response.inventory.quantity, 10)
        self.assertEqual(product_response.inventory.reserved, 0)
        self.assertEqual(product_response.category.name, "electronics")

    def test_invalid_product_request_dto(self):
        # Assert
        with self.assertRaises(ValidationError):
            ProductRequestDTO(
                sku="00056789",
                name="ear phones",
                description="something to put on your ears",
                price={"value": "invalid", "discount_percent": 0},
            )


if __name__ == "__main__":
    unittest.main()
