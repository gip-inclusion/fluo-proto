# Factory-level operator commands. Positional args: `make deploy demandes`.

# Extract positional args (everything on the command line that isn't the current target name).
# Deferred `=` (not `:=`) so `$@` is resolved at recipe-expansion time, not parse time.
ARGS = $(filter-out $@,$(MAKECMDGOALS))

# Catch-all rule: turn each positional arg into a no-op target so Make doesn't
# complain "No rule to make target 'demandes'".
%:
	@:

.PHONY: help new provision deploy dev reseed urls lint fmt update-assets

help: ## Print targets
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

new: ## Scaffold a new proto from _template — usage: make new <name>
	@proto=$(firstword $(ARGS)); \
	test -n "$$proto" || { echo "usage: make new <proto>"; exit 1; }; \
	test ! -d "prototypes/$$proto" || { echo "error: prototypes/$$proto already exists"; exit 1; }; \
	test -d "_template" || { echo "error: _template/ does not exist"; exit 1; }; \
	uvx copier copy . "prototypes/$$proto" --data proto_name="$$proto"

provision: ## Create SCW container + DB for a proto — usage: make provision <name>
	@proto=$(firstword $(ARGS)); \
	test -n "$$proto" || { echo "usage: make provision <proto>"; exit 1; }; \
	test -d "prototypes/$$proto" || { echo "error: prototypes/$$proto does not exist (run make new first)"; exit 1; }; \
	scripts/provision.sh "$$proto"

deploy: ## Build, push, and deploy one proto — usage: make deploy <name>
	@proto=$(firstword $(ARGS)); \
	test -n "$$proto" || { echo "usage: make deploy <proto>"; exit 1; }; \
	test -d "prototypes/$$proto" || { echo "error: prototypes/$$proto does not exist"; exit 1; }; \
	test -n "$$SCW_REGISTRY" || { echo "error: SCW_REGISTRY not set (source ~/.config/scw/proto-db.env or configure GH secrets)"; exit 1; }; \
	echo "Building $$proto..."; \
	docker buildx build --platform linux/amd64 \
		-t "$$SCW_REGISTRY/$$proto:latest" \
		"prototypes/$$proto" --push; \
	echo "Looking up container ID for $$proto..."; \
	container_id=$$(scw container container list name="$$proto" -o json | jq -r '.[0].id'); \
	test -n "$$container_id" && test "$$container_id" != "null" || { echo "error: no Scaleway container named $$proto"; exit 1; }; \
	echo "Deploying container $$container_id..."; \
	scw container container deploy "$$container_id" region=fr-par

dev: ## Run a proto locally with hot reload — usage: make dev <name>
	@proto=$(firstword $(ARGS)); \
	test -n "$$proto" || { echo "usage: make dev <proto>"; exit 1; }; \
	test -d "prototypes/$$proto" || { echo "error: prototypes/$$proto does not exist"; exit 1; }; \
	cd "prototypes/$$proto" && \
	docker compose up -d && \
	DATABASE_URL="postgresql+psycopg://$$proto:$$proto@localhost:5432/$$proto" \
		uv run uvicorn web.app:app --reload --host 0.0.0.0 --port 8002

reseed: ## Drop + reseed a proto's local DB — usage: make reseed <name>
	@proto=$(firstword $(ARGS)); \
	test -n "$$proto" || { echo "usage: make reseed <proto>"; exit 1; }; \
	test -d "prototypes/$$proto" || { echo "error: prototypes/$$proto does not exist"; exit 1; }; \
	cd "prototypes/$$proto" && \
	docker compose up -d && \
	sleep 2 && \
	docker compose exec -T db psql -U "$$proto" -d "$$proto" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" && \
	DATABASE_URL="postgresql+psycopg://$$proto:$$proto@localhost:5432/$$proto" \
		uv run python -m web.seed

urls: ## Print all proto names and their Scaleway URLs
	@scw container container list -o json | jq -r '.[] | "\(.name)\t\(.domain_name)"'

lint: ## Run ruff lint + format check on all protos and the template
	@uvx ruff check prototypes/ _template/
	@uvx ruff format --check prototypes/ _template/

fmt: ## Run ruff format on all protos and the template
	@uvx ruff format prototypes/ _template/

update-assets: ## Refresh _template/web/static from a les-emplois clone — usage: make update-assets <path>
	@path=$(firstword $(ARGS)); \
	test -n "$$path" || { echo "usage: make update-assets <path-to-les-emplois>"; exit 1; }; \
	test -d "$$path" || { echo "error: $$path does not exist"; exit 1; }; \
	scripts/fetch-assets.sh "$$path"
