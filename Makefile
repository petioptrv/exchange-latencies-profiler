ROOT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

docker-build-local:
	docker compose -f docker-compose.base.yml -f docker-compose.local.yml --env-file .env-local build

docker-start-local:
	docker compose -f docker-compose.base.yml -f docker-compose.local.yml --env-file .env-local up -d

docker-stop-local:
	docker compose -f docker-compose.base.yml -f docker-compose.local.yml --env-file .env-local stop

docker-build-infra-local:
	docker compose -f docker-compose.infra.base.yml -f docker-compose.infra.local.yml --env-file .env-local build

docker-start-infra-local:
	docker compose -f docker-compose.infra.base.yml -f docker-compose.infra.local.yml --env-file .env-local up -d

docker-stop-infra-local:
	docker compose -f docker-compose.infra.base.yml -f docker-compose.infra.local.yml --env-file .env-local stop

alembic-generate-migration-dev:
	export $$(grep -v '^#' .env-dev | xargs) && \
	alembic revision --autogenerate -m "$(message)" && \
	git add $$(ls -t migrations/versions/*.py | head -n1)

alembic-upgrade-head-dev:
	export $$(grep -v '^#' .env-dev | xargs) && alembic upgrade head

