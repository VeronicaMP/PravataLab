#!/bin/bash
set -e

echo "🚀 Starting Jekyll local development environment..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

echo "📦 Building and starting the container..."
docker compose up --build
