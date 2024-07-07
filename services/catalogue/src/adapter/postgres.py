import logging

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
from src.domain.value_objects import Category, Inventory, Price
from src.port.repositories import ProductRepository

config = get_config()
logger = logging.getLogger("app")


class ProductPostgresAdapter(ProductRepository):
    def __init__(self, database_url) -> None:
        self.__engine = create_engine(database_url)
        self._metadata = MetaData(schema="catalogue")

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

        self.__category_table = Table(
            "Category",
            self._metadata,
            Column("id", UUID, primary_key=True),
            Column("name", String(255), nullable=False, unique=True),
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
            Column("category_id", UUID, ForeignKey("Category.id")),
        )

        self.__session = sessionmaker(autocommit=False, bind=self.__engine)

    @property
    def metadata(self) -> MetaData:
        return self._metadata

    def create_product(
        self,
        product: Product,
        on_duplicate_sku: Exception,
        on_not_found: Exception,
    ) -> Product:
        session = self.__session()
        try:
            session.begin()
            price_id = None
            inventory_id = None
            category_id = None
            if product.price:
                insert_price = insert(self.__price_table).values(
                    id=product.price.id,
                    value=product.price.value,
                    discount_percent=product.price.discount_percent,
                )
                price_result = session.execute(insert_price)
                if not hasattr(price_result, "inserted_primary_key"):
                    raise on_not_found
                price_id = price_result.inserted_primary_key[0]

            if product.inventory:
                insert_inventory = insert(self.__inventory_table).values(
                    id=product.inventory.id,
                    quantity=product.inventory.quantity,
                    reserved=product.inventory.reserved,
                )
                inventory_result = session.execute(insert_inventory)
                if not hasattr(inventory_result, "inserted_primary_key"):
                    raise on_not_found
                inventory_id = inventory_result.inserted_primary_key[0]

            if product.category:
                get_category = select(self.__category_table.c.id).where(
                    self.__category_table.c.name == product.category.name
                )
                category_id = session.execute(get_category).fetchone()
                if category_id is None:
                    insert_category = insert(self.__category_table).values(
                        id=product.category.id, name=product.category.name
                    )
                    category_result = session.execute(insert_category)
                    if not hasattr(category_result, "inserted_primary_key"):
                        raise on_not_found
                    category_id = category_result.inserted_primary_key[0]

            logger.info("Inserting")
            insert_product = insert(self.__product_table).values(
                id=product.id,
                version=0,
                sku=product.sku,
                name=product.name,
                description=product.description,
                image_url=product.image_url,
                price_id=price_id,
                inventory_id=inventory_id,
                category_id=category_id,
            )
            session.execute(insert_product)
            session.commit()
            logger.info(f"Product sku {product.sku} created")
            return self.get_product_by_sku(
                product.sku, on_not_found=on_not_found
            )
        except IntegrityError as error:
            logger.error(error)
            session.rollback()
            raise on_duplicate_sku
        except Exception as error:
            logger.error(error)
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
                self.__category_table,
            )
            .select_from(
                self.__product_table.outerjoin(
                    self.__price_table,
                    self.__product_table.c.price_id == self.__price_table.c.id,
                )
                .outerjoin(
                    self.__inventory_table,
                    self.__product_table.c.inventory_id
                    == self.__inventory_table.c.id,
                )
                .outerjoin(
                    self.__category_table,
                    self.__product_table.c.category_id
                    == self.__category_table.c.id,
                )
            )
            .where(self.__product_table.c.sku == sku)
        )

        with self.__engine.connect() as connection:
            try:
                result = connection.execute(query).fetchone()
                if result is None:
                    logger.error(f"Product not found for {sku}")
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
                category_column_names = [
                    column.name for column in self.__category_table.c
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
                            + len(price_column_names) : len(
                                product_column_names
                            )
                            + len(price_column_names)
                            + len(inventory_column_names)
                        ],
                    )
                )
                category_dict = dict(
                    zip(
                        category_column_names,
                        result[
                            len(product_column_names)
                            + len(price_column_names)
                            + len(inventory_column_names) : len(
                                product_column_names
                            )
                            + len(price_column_names)
                            + len(inventory_column_names)
                            + len(category_column_names)
                        ],
                    )
                )
                inventory = (
                    Inventory(**inventory_dict)
                    if inventory_dict.get("id")
                    else None
                )
                price = Price(**price_dict) if price_dict.get("id") else None
                category = (
                    Category(**category_dict)
                    if category_dict.get("id")
                    else None
                )
                product = Product(
                    **product_dict,
                    price=price,
                    inventory=inventory,
                    category=category,
                )
                return product

            except NoResultFound as error:
                logger.error(error)
                raise on_not_found
            except Exception as error:
                logger.error(error)
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
        session = self.__session()
        try:
            session.begin()
            query = select(self.__product_table.c.version).where(
                self.__product_table.c.sku == product.sku
            )
            result = session.execute(query).fetchone()

            if result is None:
                raise on_not_found
            version = result[0]
            new_version = version + 1

            update_product_query = (
                update(self.__product_table)
                .where(
                    self.__product_table.c.sku == product.sku,
                    self.__product_table.c.version == version,
                )
                .values(
                    name=product.name,
                    description=product.description,
                    image_url=product.image_url,
                    version=new_version,
                )
            )
            product_result = session.execute(update_product_query)

            if (
                hasattr(product_result, "rowcount")
                and product_result.rowcount == 0
            ):
                raise on_outdated_version

            if product.price:
                price_update_query = (
                    update(self.__price_table)
                    .where(
                        self.__price_table.c.id
                        == select(self.__product_table.c.price_id).where(
                            self.__product_table.c.sku == product.sku
                        )
                    )
                    .values(
                        value=product.price.value,
                        discount_percent=product.price.discount_percent,
                    )
                )
                session.execute(price_update_query)

            if product.inventory:
                inventory_update_query = (
                    update(self.__inventory_table)
                    .where(
                        self.__inventory_table.c.id
                        == select(self.__product_table.c.inventory_id).where(
                            self.__product_table.c.sku == product.sku
                        )
                    )
                    .values(
                        quantity=product.inventory.quantity,
                        reserved=product.inventory.reserved,
                    )
                )
                session.execute(inventory_update_query)
            if product.category:
                category_update_query = (
                    update(self.__category_table)
                    .where(
                        self.__category_table.c.id
                        == select(self.__product_table.c.category_id).where(
                            self.__product_table.c.sku == product.sku
                        )
                    )
                    .values(name=product.category.name)
                )
                session.execute(category_update_query)
            session.commit()
            return self.get_product_by_sku(
                sku=product.sku, on_not_found=on_not_found
            )
        except IntegrityError as error:
            session.rollback()
            error_orig = error.orig
            if not error_orig:
                raise
            if error_orig and error_orig.args[0] == 1062:
                raise on_duplicate
            elif error_orig and error_orig.args[0] == 1452:
                raise on_not_found
            logger.error(f"SQL Error code: {error_orig.args[0]}")
            raise
        except Exception as error:
            session.rollback()
            if (
                type(error) is type(on_not_found)
                or type(error) is type(on_outdated_version)
                or type(error) is type(on_duplicate)
            ):
                raise
            raise DatabaseException(
                {
                    "code": "database.error.update",
                    "message": f"Error updating the product: {error}",
                }
            )
        finally:
            session.close()

    def delete_product(self, sku, on_not_found: Exception) -> bool:
        session = self.__session()
        try:
            session.begin()
            query = select(
                self.__product_table.c.id,
                self.__product_table.c.inventory_id,
                self.__product_table.c.price_id,
                self.__product_table.c.category_id,
            ).where(self.__product_table.c.sku == sku)
            result = session.execute(query).fetchone()
            if result is None:
                raise on_not_found

            product_id, inventory_id, price_id, category_id = result

            delete_product_query = self.__product_table.delete().where(
                self.__product_table.c.sku == sku
            )
            session.execute(delete_product_query)

            if inventory_id is not None:
                delete_inventory_query = self.__inventory_table.delete().where(
                    self.__inventory_table.c.id == inventory_id
                )
                session.execute(delete_inventory_query)

            if price_id is not None:
                delete_price_query = self.__price_table.delete().where(
                    self.__price_table.c.id == price_id
                )
                session.execute(delete_price_query)

            if category_id is not None:
                delete_category_query = self.__category_table.delete().where(
                    self.__category_table.c.id == category_id
                )
                session.execute(delete_category_query)
            session.commit()
            return True
        except Exception as error:
            logger.error(error)
            session.rollback()
            if type(error) is type(on_not_found):
                raise
            raise DatabaseException(
                {
                    "code": "database.error.delete",
                    "message": f"Error deleting product: {error}",
                }
            )
        finally:
            session.close()
