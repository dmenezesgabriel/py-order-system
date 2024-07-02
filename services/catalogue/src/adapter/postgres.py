import logging
from typing import Optional

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
from src.adapter.exceptions import DatabaseException
from src.config import get_config
from src.domain.entities import Product
from src.domain.value_objects import Inventory, Price
from src.port.repositories import ProductRepository

config = get_config()
logger = logging.getLogger("app")


class ProductPostgresAdapter(ProductRepository):
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

    def create_product(
        self,
        product: Product,
        on_duplicate_sku: Exception,
    ):
        session = self.__session()
        try:
            session.begin()
            price_id = None
            inventory_id = None
            if product.price:
                insert_price = insert(self.__price_table).values(
                    id=product.price.id,
                    value=product.price.value,
                    discount_percent=product.price.discount_percent,
                )
                price_result = session.execute(insert_price)
                price_id = price_result.inserted_primary_key[0]

            if product.inventory:
                insert_inventory = insert(self.__inventory_table).values(
                    id=product.inventory.id,
                    quantity=product.inventory.quantity,
                    reserved=product.inventory.reserved,
                )
                inventory_result = session.execute(insert_inventory)
                inventory_id = inventory_result.inserted_primary_key[0]

            insert(self.__product_table).values(
                id=product.id,
                version=0,
                sku=product.sku,
                name=product.name,
                description=product.description,
                image_url=product.image_url,
                price_id=price_id,
                inventory_id=inventory_id,
            )
            session.commit()
            logger.info("Product created")
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

    def get_product_by_sku(self, sku: str, on_not_found: Exception) -> Product:
        query = (
            select(
                self.__product_table,
                self.__price_table,
                self.__inventory_table,
            )
            .select_from(
                self.__product_table.outerjoin(
                    self.__price_table,
                    self.__product_table.c.price_id == self.__price_table.c.id,
                ).outerjoin(
                    self.__inventory_table,
                    self.__product_table.c.inventory_id
                    == self.__inventory_table.c.id,
                )
            )
            .where(self.__product_table.c.sku == sku)
        )

        with self.__engine.connect() as connection:
            try:
                result = connection.execute(query).fetchone()
                if result is None:
                    raise on_not_found

                product_column_names = [
                    column.name for column in self.__product_table.c
                ]
                price_column_names = [
                    column.name for column in self.__price_table.c
                ]
                inventory_column_names = [
                    column.name for column in self.__inventory_table.c
                ]
                product_dict = dict(
                    zip(
                        product_column_names,
                        result[0 : len(product_column_names)],
                    )
                )
                price_dict = dict(
                    zip(
                        price_column_names,
                        result[
                            len(product_column_names) : len(
                                product_column_names
                            )
                            + len(price_column_names)
                        ],
                    )
                )
                inventory_dict = dict(
                    zip(
                        inventory_column_names,
                        result[
                            len(product_column_names)
                            + len(price_column_names) :
                        ],
                    )
                )
                inventory = (
                    Inventory(**inventory_dict)
                    if inventory_dict.get("id")
                    else None
                )
                price = Price(**price_dict) if price_dict.get("id") else None
                product = Product(
                    **product_dict, price=price, inventory=inventory
                )
                return product

            except NoResultFound:
                raise on_not_found
            except Exception as error:
                if type(error) is type(on_not_found):
                    raise

                raise DatabaseException(
                    {
                        "code": "database.error.select",
                        "message": f"Error searching product by sku :{error}",
                    }
                )

    def update_product(
        self,
        product: Product,
        on_not_found: Exception,
        on_outdated_version: Exception,
        on_duplicate: Exception,
    ) -> Product:
        """ """
        pass

    def delete_product(self, sku, on_not_found: Exception) -> bool:
        """ """
        return True
