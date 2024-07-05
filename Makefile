clean: |
	sh scripts/clean.sh

create-catalogue-migration: |
	@read -p "Enter migration message: " MESSAGE; \
	docker compose run --rm catalogue-migrations /bin/bash -c "alembic -c migrations/alembic/alembic.ini revision --autogenerate -m '$$MESSAGE'"

apply-catalogue-migrations: |
	docker compose run --rm catalogue-migrations
