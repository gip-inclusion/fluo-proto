#!/bin/bash
# Create a Scaleway Serverless Container + PostgreSQL database for a new proto.
# Usage: scripts/provision.sh <proto_name>
#
# Reads credentials from ~/.config/scw/proto-db.env:
#   SCW_REGISTRY, PROTO_DB_INSTANCE_ID, PROTO_DB_ENDPOINT, SCW_NAMESPACE_ID
#
# Reads SCW secret key from `scw config get secret-key`.

set -euo pipefail

proto="${1:?usage: $0 <proto_name>}"

# shellcheck disable=SC1090
source ~/.config/scw/proto-db.env

: "${SCW_REGISTRY:?SCW_REGISTRY not set in ~/.config/scw/proto-db.env}"
: "${PROTO_DB_INSTANCE_ID:?PROTO_DB_INSTANCE_ID not set}"
: "${PROTO_DB_ENDPOINT:?PROTO_DB_ENDPOINT not set (format: host:port)}"
: "${SCW_NAMESPACE_ID:?SCW_NAMESPACE_ID not set (Scaleway Serverless Container namespace UUID)}"

PROTO_DB_HOST="${PROTO_DB_ENDPOINT%:*}"
PROTO_DB_PORT="${PROTO_DB_ENDPOINT##*:}"

SCW_SECRET_KEY=$(scw config get secret-key)

echo "Provisioning proto: $proto"

# 1. Create DB user with random password
db_password=$(openssl rand -hex 24)
echo "Creating database user '$proto'..."
scw rdb user create instance-id="$PROTO_DB_INSTANCE_ID" name="$proto" password="$db_password"

# 2. Create database
echo "Creating database '$proto'..."
scw rdb database create instance-id="$PROTO_DB_INSTANCE_ID" name="$proto"

# 3. Grant privileges
echo "Granting privileges..."
scw rdb privilege set instance-id="$PROTO_DB_INSTANCE_ID" database-name="$proto" user-name="$proto" permission=all

# 4. Pre-seed the image tag (container create fails if image doesn't exist)
echo "Building and pushing initial image..."
docker login "${SCW_REGISTRY%%/*}" -u nologin -p "$SCW_SECRET_KEY"
docker buildx build --platform linux/amd64 \
  -t "$SCW_REGISTRY/$proto:latest" \
  "prototypes/$proto" --push

# 5. Create the Serverless Container
database_url="postgresql+psycopg://$proto:$db_password@$PROTO_DB_HOST:$PROTO_DB_PORT/$proto"
echo "Creating Scaleway Serverless Container '$proto'..."
scw container container create \
  namespace-id="$SCW_NAMESPACE_ID" \
  region=fr-par \
  name="$proto" \
  registry-image="$SCW_REGISTRY/$proto:latest" \
  min-scale=1 \
  max-scale=1 \
  memory-limit=256 \
  cpu-limit=140 \
  privacy=public \
  port=8080 \
  protocol=http1 \
  environment-variables.DATABASE_URL="$database_url" \
  -o json > "/tmp/proto-container-$proto.json"

container_id=$(jq -r '.id' "/tmp/proto-container-$proto.json")
domain_name=$(jq -r '.domain_name' "/tmp/proto-container-$proto.json")
rm "/tmp/proto-container-$proto.json"

echo
echo "Provisioned:"
echo "  container_id: $container_id"
echo "  public URL:   https://$domain_name"
echo "  DB:           $proto"
echo
echo "Run 'make deploy $proto' to trigger the first real deploy."
