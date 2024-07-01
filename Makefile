# TODO add wild card commit name
create-catalogue-migration: |
	docker compose run --rm catalogue-migrations /bin/bash -c "alembic -c migrations/alembic/alembic.ini revision --autogenerate -m 'initial migration'"
