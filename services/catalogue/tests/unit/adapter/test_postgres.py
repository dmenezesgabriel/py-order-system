import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from src.adapter.exceptions import DatabaseException
from src.adapter.postgres import ProductPostgresAdapter
from src.domain.entities import Product
from src.domain.value_objects import Category, Inventory, Price


class TestProductPostgresAdapter(unittest.TestCase):

    @patch("src.adapter.postgres.create_engine")
    @patch("src.adapter.postgres.MetaData")
    @patch("src.adapter.postgres.sessionmaker")
    def setUp(self, mock_sessionmaker, mock_metadata, mock_engine):
        self.mock_engine = mock_engine
        self.mock_metadata = mock_metadata
        self.mock_sessionmaker = mock_sessionmaker
        mock_db_url = "mock_db_url"
        self.adapter = ProductPostgresAdapter(mock_db_url)

    @patch("src.adapter.postgres.create_engine")
    @patch("src.adapter.postgres.MetaData")
    @patch("src.adapter.postgres.sessionmaker")
    def should_init_adapter(
        self, mock_sessionmaker: Mock, mock_metadata: Mock, mock_engine: Mock
    ):
        # Arrange
        mock_db_url = "mock_db_url"

        # Act
        self.adapter = ProductPostgresAdapter(mock_db_url)

        # Assert
        mock_sessionmaker.assert_called_once()
        mock_metadata.assert_called_once()
        mock_engine.assert_called_once()

    def test_should_create_product(self):
        # Arrange
        mock_product = Product(
            id=uuid4(),
            sku="test_sku",
            name="Test Product",
            description="Test Description",
            image_url="http://example.com/image.png",
            price=Price(id=uuid4(), value=100.0, discount_percent=0.0),
            inventory=Inventory(id=uuid4(), quantity=10, reserved=0),
            category=Category(id=uuid4(), name="Test Category"),
        )
        self.mock_sessionmaker.return_value.execute.return_value = Mock(
            inserted_primary_key=[mock_product.id]
        )
        self.adapter.get_product_by_sku = Mock(return_value=mock_product)

        # Act
        created_product = self.adapter.create_product(
            mock_product, on_duplicate_sku=Exception, on_not_found=Exception
        )

        # Assert
        self.assertEqual(
            self.mock_sessionmaker.return_value().execute.call_count, 4
        )
        self.adapter.get_product_by_sku.assert_called_once()
        self.assertEqual(created_product.sku, mock_product.sku)
        self.assertEqual(created_product.name, mock_product.name)
        self.assertEqual(created_product.description, mock_product.description)
        self.assertEqual(created_product.image_url, mock_product.image_url)
        self.assertEqual(created_product.price.value, mock_product.price.value)
        self.assertEqual(
            created_product.inventory.quantity, mock_product.inventory.quantity
        )
        self.assertEqual(
            created_product.inventory.reserved, mock_product.inventory.reserved
        )
        self.assertEqual(
            created_product.category.name, mock_product.category.name
        )

    def test_should_handle_create_product_database_exception(self):
        # Arrange
        mock_product = Product(
            id=uuid4(),
            sku="test_sku",
            name="Test Product",
            description="Test Description",
            image_url="http://example.com/image.png",
            price=Price(id=uuid4(), value=100.0, discount_percent=0.0),
            inventory=Inventory(id=uuid4(), quantity=10, reserved=0),
            category=Category(id=uuid4(), name="Test Category"),
        )
        self.mock_sessionmaker.return_value.execute.side_effect = Exception(
            "Mock DB Error"
        )

        # Act & Assert
        with self.assertRaises(DatabaseException):
            self.adapter.create_product(
                mock_product,
                on_duplicate_sku=Exception,
                on_not_found=Exception,
            )

        self.assertEqual(
            self.mock_sessionmaker.return_value().rollback.call_count, 1
        )

    def test_should_handle_create_product_integrity_error(self):
        # Arrange
        mock_product = Product(
            id=uuid4(),
            sku="test_sku",
            name="Test Product",
            description="Test Description",
            image_url="http://example.com/image.png",
            price=Price(id=uuid4(), value=100.0, discount_percent=0.0),
            inventory=Inventory(id=uuid4(), quantity=10, reserved=0),
            category=Category(id=uuid4(), name="Test Category"),
        )
        self.mock_sessionmaker.return_value.execute.side_effect = (
            IntegrityError(params=[], orig=Exception, statement="")
        )

        # Act & Assert
        with self.assertRaises(Exception):
            self.adapter.create_product(
                mock_product,
                on_duplicate_sku=Exception,
                on_not_found=Exception,
            )

        self.assertEqual(
            self.mock_sessionmaker.return_value().rollback.call_count, 1
        )

    def test_should_get_product_by_sku(self):
        # Arrange
        id_ = uuid4()
        self.mock_sessionmaker.return_value().execute.return_value = (
            id_,
            "123456",
            "test_name",
            "test_description",
            "http://test.com/image.png",
        )

        with patch.object(
            self.adapter, "product_table_columns"
        ) as mock_columns:
            mock_columns.return_value = [
                "id",
                "sku",
                "name",
                "description",
                "image_url",
            ]

            # Act
            result = self.adapter.get_product_by_sku(
                "123456", on_not_found=Exception
            )

        # Assert
        self.assertEqual(result.id, id_)
        self.assertEqual(result.sku, "123456")
        self.assertEqual(result.name, "test_name")


if __name__ == "__main__":
    unittest.main()
