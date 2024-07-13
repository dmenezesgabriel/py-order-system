import unittest
from unittest.mock import Mock, patch

from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.exc import IntegrityError, NoResultFound
from src.adapter.exceptions import DatabaseException
from src.adapter.postgres import ProductPostgresAdapter
from tests.helpers.product import ProductHelper


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
        mock_product = ProductHelper.create_product()
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

    def test_should_handle_create_product_insert_price_fail(self):
        # Arrange
        mock_product = ProductHelper.create_product()
        self.mock_sessionmaker.return_value.execute.return_value = Mock(
            inserted_primary_key=[mock_product.id]
        )
        self.adapter.get_product_by_sku = Mock(return_value=mock_product)
        mock_row = Mock(spec=CursorResult)
        mock_row.inserted_primary_key = "id"

        self.mock_sessionmaker.return_value().execute.side_effect = [
            None,
            mock_row,
            mock_row,
            mock_row,
        ]

        # Act & Assert
        with self.assertRaises(DatabaseException):
            self.adapter.create_product(
                mock_product,
                on_duplicate_sku=Exception,
                on_not_found=Exception,
            )

        # Assert
        self.assertEqual(
            self.mock_sessionmaker.return_value().execute.call_count, 1
        )

    def test_should_handle_create_product_insert_inventory_fail(self):
        # Arrange
        mock_product = ProductHelper.create_product()
        self.mock_sessionmaker.return_value.execute.return_value = Mock(
            inserted_primary_key=[mock_product.id]
        )
        self.adapter.get_product_by_sku = Mock(return_value=mock_product)
        mock_row = Mock(spec=CursorResult)
        mock_row.inserted_primary_key = "id"

        self.mock_sessionmaker.return_value().execute.side_effect = [
            mock_row,
            None,
            mock_row,
            mock_row,
        ]

        # Act & Assert
        with self.assertRaises(DatabaseException):
            self.adapter.create_product(
                mock_product,
                on_duplicate_sku=Exception,
                on_not_found=Exception,
            )

        # Assert
        self.assertEqual(
            self.mock_sessionmaker.return_value().execute.call_count, 2
        )

    def test_should_handle_create_product_insert_category_fail(self):
        # Arrange
        mock_product = ProductHelper.create_product()
        self.mock_sessionmaker.return_value.execute.return_value = Mock(
            inserted_primary_key=[mock_product.id]
        )
        self.adapter.get_product_by_sku = Mock(return_value=mock_product)
        mock_row = Mock(spec=CursorResult)
        mock_row.inserted_primary_key = "id"

        self.mock_sessionmaker.return_value().execute.side_effect = [
            mock_row,
            mock_row,
            None,
            mock_row,
        ]

        # Act & Assert
        with self.assertRaises(DatabaseException):
            self.adapter.create_product(
                mock_product,
                on_duplicate_sku=Exception,
                on_not_found=Exception,
            )

        # Assert
        self.assertEqual(
            self.mock_sessionmaker.return_value().execute.call_count, 3
        )

    def test_should_handle_create_product_database_exception(self):
        # Arrange
        mock_product = ProductHelper.create_product()
        fetchone = (
            self.mock_sessionmaker.return_value().execute.return_value.fetchone
        )
        fetchone.side_effect = Exception("Mock DB Error")

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
        mock_product = ProductHelper.create_product()
        fetchone = (
            self.mock_sessionmaker.return_value().execute.return_value.fetchone
        )
        fetchone.side_effect = IntegrityError(
            params=[], orig=Exception, statement=""
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
        mock_product = ProductHelper.create_product()
        mock_product_tuple = ProductHelper.create_product_tuple(
            product=mock_product
        )
        self.mock_sessionmaker.return_value().execute.return_value.fetchone = (
            Mock(return_value=mock_product_tuple)
        )

        # Act
        product = self.adapter.get_product_by_sku(
            sku="test_sku", on_not_found=Exception
        )

        # Assert
        self.assertEqual(product.sku, mock_product.sku)
        self.assertEqual(product.name, mock_product.name)
        self.assertEqual(product.description, mock_product.description)
        self.assertEqual(product.image_url, mock_product.image_url)
        self.assertEqual(product.price.value, mock_product.price.value)
        self.assertEqual(
            product.inventory.quantity, mock_product.inventory.quantity
        )
        self.assertEqual(
            product.inventory.reserved, mock_product.inventory.reserved
        )
        self.assertEqual(product.category.name, mock_product.category.name)

    def test_should_handle_get_product_by_sku_no_result_found(self):
        # Arrange
        fetchone = (
            self.mock_sessionmaker.return_value().execute.return_value.fetchone
        )
        fetchone.side_effect = NoResultFound()

        # Act & Assert
        with self.assertRaises(Exception):
            self.adapter.get_product_by_sku(
                sku="test_sku",
                on_not_found=Exception,
            )

    def test_should_handle_get_product_by_sku_generic_exception(self):
        # Arrange
        fetchone = (
            self.mock_sessionmaker.return_value().execute.return_value.fetchone
        )
        fetchone.side_effect = Exception()

        # Act & Assert
        with self.assertRaises(DatabaseException):
            self.adapter.get_product_by_sku(
                sku="test_sku",
                on_not_found=Exception,
            )


if __name__ == "__main__":
    unittest.main()
