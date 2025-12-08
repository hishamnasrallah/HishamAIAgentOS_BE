#!/bin/bash
# Database Backup Script
# Usage: ./backup_database.sh [backup_name]

set -e

BACKUP_NAME=${1:-backup-$(date +%Y%m%d-%H%M%S)}
NAMESPACE=${NAMESPACE:-hishamos}

echo "💾 Creating database backup: $BACKUP_NAME"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check prerequisites
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl not found${NC}"
    exit 1
fi

# Get database credentials from secret
echo -e "${YELLOW}Retrieving database credentials...${NC}"

DB_USER=$(kubectl get secret hishamos-secrets -n $NAMESPACE -o jsonpath='{.data.POSTGRES_USER}' | base64 -d)
DB_PASSWORD=$(kubectl get secret hishamos-secrets -n $NAMESPACE -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d)
DB_NAME=$(kubectl get secret hishamos-secrets -n $NAMESPACE -o jsonpath='{.data.POSTGRES_DB}' | base64 -d)

# Create backup
echo -e "${YELLOW}Creating backup...${NC}"

kubectl exec -n $NAMESPACE deployment/postgres -- \
    env PGPASSWORD=$DB_PASSWORD \
    pg_dump -U $DB_USER $DB_NAME > "$BACKUP_NAME.sql"

# Compress backup
echo -e "${YELLOW}Compressing backup...${NC}"
gzip "$BACKUP_NAME.sql"

BACKUP_SIZE=$(du -h "$BACKUP_NAME.sql.gz" | cut -f1)

echo -e "${GREEN}✓ Backup created: $BACKUP_NAME.sql.gz (Size: $BACKUP_SIZE)${NC}"

# Optional: Upload to S3 or other storage
if [ -n "$BACKUP_S3_BUCKET" ]; then
    echo -e "${YELLOW}Uploading to S3...${NC}"
    aws s3 cp "$BACKUP_NAME.sql.gz" "s3://$BACKUP_S3_BUCKET/backups/$BACKUP_NAME.sql.gz"
    echo -e "${GREEN}✓ Backup uploaded to S3${NC}"
fi

echo -e "${GREEN}✅ Database backup completed successfully!${NC}"

