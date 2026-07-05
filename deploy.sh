#!/bin/bash
echo "============================================="
echo "Deploying GuardianAI Security Guardrails Node"
echo "============================================="

# Ensure docker daemon is active
if ! docker info >/dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and retry."
    exit 1
fi

echo "[1/3] Tearing down existing containers..."
docker-compose down

echo "[2/3] Building new container modules..."
docker-compose build

echo "[3/3] Launching GuardianAI services in background..."
docker-compose up -d

echo "============================================="
echo "GuardianAI Deployed Successfully!"
echo "---------------------------------------------"
echo "Frontend: http://localhost:3000"
echo "Backend:  http://127.0.0.1:8000"
echo "============================================="
