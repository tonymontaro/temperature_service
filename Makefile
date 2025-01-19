KUB_CONGIG_FILES = kubernetes/config
KUB_FILES = kubernetes/app

define run_development_command
	docker-compose -f docker-compose.yml run service bash -c $(1)
endef

define run_test_command
	docker-compose -f test.docker-compose.yml run service bash -c $(1) ; \
	docker-compose -f test.docker-compose.yml down --remove-orphans
endef

# Manage db migrations with alembic. TODO: Ensure generated index doesn't get deleted.
.PHONY: db_migration
db_migration:
	@echo "Enter a name for the migration script: "; \
    read script_name; \
    $(call run_development_command,"alembic upgrade head && alembic revision -m \"$$script_name\" --autogenerate")

.PHONY: build
build: 
	docker-compose -f docker-compose.yml build

## Run unit tests
.PHONY: test
test:
	$(call run_test_command,"alembic upgrade head && python -m pytest -rf tests/ -vv")

## Start the application in development mode
.PHONY: run
run: 
	docker-compose -f docker-compose.yml up

.PHONY: kub_apply
kub_apply:
	kubectl apply -f $(KUB_CONGIG_FILES)
	kubectl apply -f $(KUB_FILES)

.PHONY: kub_delete
kub_delete:
	kubectl delete -f $(KUB_FILES)
	kubectl delete -f $(KUB_CONGIG_FILES)
