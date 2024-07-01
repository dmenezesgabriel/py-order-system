from typing import Optional

from adapter.exceptions import DatabaseException
from domain.entities import Product
from domain.value_objects import Inventory, Price
from port.repositories import ProductRepository
from sqlalchemy import (
    UUID,
    Column,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
    create_engine,
    insert,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import sessionmaker


class ProductMySQLAdapter(ProductRepository):
    def __init__(self, database_url) -> None:
        self.__engine = create_engine(database_url)
        self._metadata = MetaData()

        self.__inventory_table = Table(
            "Inventory",
            self._metadata,
            Column("id", UUID, primary_key=True),
            Column("quantity", Integer, nullable=False),
            Column("reserved", Integer, nullable=False, default=0),
        )

        self.__price_table = Table(
            "Price",
            self._metadata,
            Column("id", UUID, primary_key=True),
            Column("value", Float, nullable=False),
            Column("discount_percent", Float, nullable=False),
        )

        self.__product_table = Table(
            "Product",
            self._metadata,
            Column("id", UUID, primary_key=True),
            Column("version", Integer, nullable=False, default=0),
            Column("sku", String(50), nullable=False, unique=True),
            Column("name", String(255), nullable=False),
            Column("description", Text, nullable=False),
            Column("image_url", String(255), nullable=False),
            Column("price_id", UUID, ForeignKey("Price.id")),
            Column("inventory_id", UUID, ForeignKey("Inventory.id")),
        )

        self.__session = sessionmaker(autocommit=False, bind=self.__engine)

    @property
    def metadata(self) -> MetaData:
        return self._metadata

    def insert(self, product: Product, on_duplicate_sku: Exception):
        session = self.__session()
        try:
            session.begin()
            price_id = None
            inventory_id = None
            if product.price:
                insert_price = insert(self.__price_table).values(
                    value=product.price.value,
                    discount_percent=product.price.discount_percent,
                )
                price_result = session.execute(insert_price)
                price_id = price_result.inserted_primary_key[0]

            if product.inventory:
                insert_inventory = insert(self.__inventory_table).values(
                    quantity=product.inventory.quantity,
                    reserved=product.inventory.reserved,
                )
                inventory_result = session.execute(insert_inventory)
                inventory_id = inventory_result.inserted_primary_key[0]

            insert_product = insert(self.__product_table).values(
                version=0,
                sku=product.sku,
                name=product.name,
                description=product.description,
                image_url=product.image_url,
                price_id=price_id,
                inventory_id=inventory_id,
            )
            session.execute(insert_product)
            session.commit()
        except IntegrityError:
            session.rollback()
            raise on_duplicate_sku
        except Exception as error:
            session.rollback()
            if type(error) is type(on_duplicate_sku):
                raise
            raise DatabaseException(
                {
                    "code": "database.error.insert",
                    "message": f"Error inserting product in database {error}",
                }
            )
        finally:
            session.close()
