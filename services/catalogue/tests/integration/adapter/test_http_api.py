import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

from fastapi import HTTPException
from fastapi.testclient import TestClient
from src.adapter.dto import (
    CategoryDTO,
    InventoryDTO,
    PriceDTO,
    ProductRequestDTO,
    ProductResponseDTO,
)
from src.adapter.http_api import HTTPApiAdapter
from src.domain.entities import Category, Product
from src.domain.exceptions import (
    InvalidSku,
    OutdatedProduct,
    ProductAlreadyExist,
    ProductNotFound,
)
from src.domain.services import CatalogueService
from src.domain.value_objects import Inventory, Price


class TestHTTPApiAdapter(unittest.TestCase):

    def setUp(self) -> None:
        self.catalogue_service_mock = Mock(spec=CatalogueService)
        self.api_adapter = HTTPApiAdapter(self.catalogue_service_mock)
        self.client = TestClient(self.api_adapter.router)

    def test_should_create_product(self) -> None:
        id_ = uuid4()
        product_request = ProductRequestDTO(
            sku="123456",
            name="test_name",
            description="test_description",
            image_url="http://test.com/image.png",
            price=PriceDTO(value=100.0, discount_percent=0.5),
            inventory=InventoryDTO(quantity=10, reserved=1),
            category=CategoryDTO(name="test_category"),
        )
        created_product = Product(
            id=id_,
            sku="123456",
            name="test_name",
            description="test_description",
            image_url="http://test.com/image.png",
            price=Price(value=100.0, discount_percent=0.5),
            inventory=Inventory(quantity=10, reserved=1),
            category=Category(name="test_category"),
        )
        self.catalogue_service_mock.create_product.return_value = (
            created_product
        )

        response = self.client.post(
            "/product", json=product_request.model_dump()
        )

        expected_response = ProductResponseDTO(
            id=id_,
            sku="123456",
            name="test_name",
            description="test_description",
            image_url="http://test.com/image.png",
            price=PriceDTO(value=100.0, discount_percent=0.5),
            inventory=InventoryDTO(quantity=10, reserved=1),
            category=CategoryDTO(name="test_category"),
        ).model_dump()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {**expected_response, "id": str(expected_response["id"])},
        )

    @patch("logging.Logger.error")
    def test_create_product_invalid_sku_should_raise_http_exception(
        self, mock_logger_error: Mock
    ) -> None:
        product_request = ProductRequestDTO(
            sku="invalid_sku",
            name="test_name",
            description="test_description",
            image_url="http://test.com/image.png",
        )
        self.catalogue_service_mock.create_product.side_effect = InvalidSku(
            "Invalid SKU"
        )

        with self.assertRaises(HTTPException) as context:
            self.client.post("/product", json=product_request.model_dump())

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Invalid SKU", context.exception.detail)
        mock_logger_error.assert_called_once()

    @patch("logging.Logger.error")
    def test_create_product_should_raise_product_already_exist(
        self, mock_logger_error: Mock
    ) -> None:
        product_request = ProductRequestDTO(
            sku="duplicate_sku",
            name="test_name",
            description="test_description",
            image_url="http://test.com/image.png",
        )
        self.catalogue_service_mock.create_product.side_effect = (
            ProductAlreadyExist("Product already exists")
        )

        with self.assertRaises(HTTPException) as context:
            self.client.post("/product", json=product_request.model_dump())

        self.assertEqual(context.exception.status_code, 409)
        self.assertIn("Product already exists", context.exception.detail)
        mock_logger_error.assert_called_once()

    @patch("logging.Logger.error")
    def test_create_product_should_raise_exception(
        self, mock_logger_error: Mock
    ) -> None:
        product_request = ProductRequestDTO(
            sku="duplicate_sku",
            name="test_name",
            description="test_description",
            image_url="http://test.com/image.png",
        )
        self.catalogue_service_mock.create_product.side_effect = Exception(
            "Generic test exception"
        )

        with self.assertRaises(HTTPException) as context:
            self.client.post("/product", json=product_request.model_dump())

        self.assertEqual(context.exception.status_code, 500)
        self.assertIn(
            "Error creating product: Generic test exception",
            context.exception.detail,
        )
        mock_logger_error.assert_called_once()

    def test_should_get_product_by_sku(self) -> None:
        id_ = uuid4()
        product = Product(
            id=id_,
            sku="123456",
            name="test_name",
            description="test_description",
            image_url="http://test.com/image.png",
            price=Price(value=100.0, discount_percent=0.5),
            inventory=Inventory(quantity=10, reserved=1),
            category=Category(name="test_category"),
        )
        self.catalogue_service_mock.get_product_by_sku.return_value = product

        response = self.client.get("/product/123456")

        expected_response = ProductResponseDTO(
            id=id_,
            sku="123456",
            name="test_name",
            description="test_description",
            image_url="http://test.com/image.png",
            price=PriceDTO(value=100.0, discount_percent=0.5),
            inventory=InventoryDTO(quantity=10, reserved=1),
            category=CategoryDTO(name="test_category"),
        ).model_dump()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {**expected_response, "id": str(expected_response["id"])},
        )

    @patch("logging.Logger.error")
    def test_get_product_by_sku_should_raise_not_found(
        self, mock_logger_error: Mock
    ) -> None:
        self.catalogue_service_mock.get_product_by_sku.side_effect = (
            ProductNotFound("Product not found")
        )

        with self.assertRaises(HTTPException) as context:
            self.client.get("/product/non_existing_sku")

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("Product not found", context.exception.detail)
        mock_logger_error.assert_called_once()

    @patch("logging.Logger.error")
    def test_get_product_by_sku_should_raise_invalid_sku(
        self, mock_logger_error: Mock
    ) -> None:
        self.catalogue_service_mock.get_product_by_sku.side_effect = (
            InvalidSku("Invalid SKU")
        )

        with self.assertRaises(HTTPException) as context:
            self.client.get("/product/non_existing_sku")

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Invalid SKU", context.exception.detail)
        mock_logger_error.assert_called_once()

    @patch("logging.Logger.error")
    def test_get_product_by_sku_should_raise_generic_exception(
        self, mock_logger_error: Mock
    ) -> None:
        self.catalogue_service_mock.get_product_by_sku.side_effect = Exception(
            "Generic exception"
        )

        with self.assertRaises(HTTPException) as context:
            self.client.get("/product/non_existing_sku")

        self.assertEqual(context.exception.status_code, 500)
        self.assertIn(
            "Error getting product: Generic exception",
            context.exception.detail,
        )
        mock_logger_error.assert_called_once()

    def test_should_update_product(self) -> None:
        id_ = uuid4()
        product_request = ProductRequestDTO(
            sku="123456",
            name="updated_name",
            description="updated_description",
            image_url="http://updated.com/image.png",
            price=PriceDTO(value=150.0, discount_percent=0.5),
            inventory=InventoryDTO(quantity=15, reserved=2),
            category=CategoryDTO(name="updated_category"),
        )
        updated_product = Product(
            id=id_,
            sku="123456",
            name="updated_name",
            description="updated_description",
            image_url="http://updated.com/image.png",
            price=Price(value=150.0, discount_percent=0.5),
            inventory=Inventory(quantity=15, reserved=2),
            category=Category(name="updated_category"),
        )
        self.catalogue_service_mock.update_product.return_value = (
            updated_product
        )

        response = self.client.put(
            "/product/123456", json=product_request.model_dump()
        )

        expected_response = ProductResponseDTO(
            id=id_,
            sku="123456",
            name="updated_name",
            description="updated_description",
            image_url="http://updated.com/image.png",
            price=PriceDTO(value=150.0, discount_percent=0.5),
            inventory=InventoryDTO(quantity=15, reserved=2),
            category=CategoryDTO(name="updated_category"),
        ).model_dump()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {**expected_response, "id": str(expected_response["id"])},
        )

    @patch("logging.Logger.error")
    def test_update_product_should_raise_not_found(
        self, mock_logger_error: Mock
    ) -> None:
        product_request = ProductRequestDTO(
            sku="123456",
            name="updated_name",
            description="updated_description",
            image_url="http://updated.com/image.png",
        )
        self.catalogue_service_mock.update_product.side_effect = (
            ProductNotFound("Product not found")
        )

        with self.assertRaises(HTTPException) as context:
            self.client.put(
                "/product/non_existing_sku", json=product_request.model_dump()
            )

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("Product not found", context.exception.detail)
        mock_logger_error.assert_called_once()

    @patch("logging.Logger.error")
    def test_update_product_should_raise_invalid_sku(
        self, mock_logger_error: Mock
    ) -> None:
        product_request = ProductRequestDTO(
            sku="123456",
            name="updated_name",
            description="updated_description",
            image_url="http://updated.com/image.png",
        )
        self.catalogue_service_mock.update_product.side_effect = InvalidSku(
            "Invalid SKU"
        )

        with self.assertRaises(HTTPException) as context:
            self.client.put(
                "/product/non_existing_sku", json=product_request.model_dump()
            )

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Invalid SKU", context.exception.detail)
        mock_logger_error.assert_called_once()

    @patch("logging.Logger.error")
    def test_update_product_should_raise_outdated_product(
        self, mock_logger_error: Mock
    ) -> None:
        product_request = ProductRequestDTO(
            sku="123456",
            name="updated_name",
            description="updated_description",
            image_url="http://updated.com/image.png",
        )
        self.catalogue_service_mock.update_product.side_effect = (
            OutdatedProduct("Outdated product")
        )

        with self.assertRaises(HTTPException) as context:
            self.client.put(
                "/product/123456", json=product_request.model_dump()
            )

        self.assertEqual(context.exception.status_code, 409)
        self.assertIn("Outdated product", context.exception.detail)
        mock_logger_error.assert_called_once()

    @patch("logging.Logger.error")
    def test_update_product_should_raise_generic_exception(
        self, mock_logger_error: Mock
    ) -> None:
        product_request = ProductRequestDTO(
            sku="123456",
            name="updated_name",
            description="updated_description",
            image_url="http://updated.com/image.png",
        )
        self.catalogue_service_mock.update_product.side_effect = Exception(
            "Generic test exception"
        )

        with self.assertRaises(HTTPException) as context:
            self.client.put(
                "/product/123456", json=product_request.model_dump()
            )

        self.assertEqual(context.exception.status_code, 500)
        self.assertIn(
            "Error updating product: Generic test exception",
            context.exception.detail,
        )
        mock_logger_error.assert_called_once()

    def test_delete_product(self):
        response = self.client.delete("/product/123456")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json())

    @patch("logging.Logger.error")
    def test_delete_product_should_raise_not_found(self, mock_logger_error):
        self.catalogue_service_mock.delete_product.side_effect = (
            ProductNotFound("Product not found")
        )
        with self.assertRaises(HTTPException) as context:
            self.client.delete("/product/non_existing_sku")

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("Product not found", context.exception.detail)
        mock_logger_error.assert_called_once()

    @patch("logging.Logger.error")
    def test_delete_product_should_raise_invalid_sku(self, mock_logger_error):
        self.catalogue_service_mock.delete_product.side_effect = InvalidSku(
            "Invalid SKU"
        )
        with self.assertRaises(HTTPException) as context:
            self.client.delete("/product/non_existing_sku")

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Invalid SKU", context.exception.detail)
        mock_logger_error.assert_called_once()

    @patch("logging.Logger.error")
    def test_delete_product_should_raise_generic_exception(
        self, mock_logger_error
    ):
        self.catalogue_service_mock.delete_product.side_effect = Exception(
            "Generic test exception"
        )
        with self.assertRaises(HTTPException) as context:
            self.client.delete("/product/non_existing_sku")

        self.assertEqual(context.exception.status_code, 500)
        self.assertIn(
            "Error deleting product: Generic test exception",
            context.exception.detail,
        )
        mock_logger_error.assert_called_once()


if __name__ == "__main__":
    unittest.main()
