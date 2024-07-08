# Python Order System

## Microservices

- Product Catalogue - MySQL + redis
- Order - MySQL
- Order Management - DynamoDB
- Order Payment - DynamoDB
- Product Search - DynamoDB

## Catalogue

http://localhost:8180/docs

## Glossary

- SKU: Stock Keeping Unit

## Postgres

- **List Schemas**:

```sh
docker compose exec postgres-db /bin/bash
```

```sh
psql -U postgres
```

```sh
# database_name
\c postgres
```

```sh
# Tables
\dt
```

```sh
SELECT schema_name
FROM information_schema.schemata;
```

```sh
\dt catalogue.*
```

## Resources

- [er-diagram-for-online-shop](https://vertabelo.com/blog/er-diagram-for-online-shop/)
