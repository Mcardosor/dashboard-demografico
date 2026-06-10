#!/bin/bash
set -e

echo "==> Atualizando repositório..."
git pull origin main

echo "==> Rebuilding e subindo container..."
docker compose down
docker compose build --no-cache
docker compose up -d

echo "==> Status:"
docker compose ps

echo ""
echo "Dashboard disponível em: http://$(hostname -I | awk '{print $1}'):8501"
