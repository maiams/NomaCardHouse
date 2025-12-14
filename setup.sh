#!/bin/bash

# Noma Card House - Setup Script
# This script automates the installation process

set -e

echo "Noma Card House - Setup Script"
echo "=================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "[ERROR] Node.js version 18 or higher is required. You have version $NODE_VERSION"
    exit 1
fi

echo "[OK] Node.js $(node -v) detected"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "[WARNING] Docker is not installed. Database setup will be skipped."
    echo "         Please install Docker or configure PostgreSQL manually."
    SKIP_DOCKER=true
else
    echo "[OK] Docker detected"
    SKIP_DOCKER=false
fi

echo ""
echo "Installing dependencies..."
npm install

echo ""
echo "Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "[OK] Created .env file"
    echo "[INFO] Please edit .env with your configuration (Stripe keys, etc.)"
else
    echo "[INFO] .env file already exists, skipping..."
fi

if [ "$SKIP_DOCKER" = false ]; then
    echo ""
    echo "Starting PostgreSQL with Docker..."
    docker-compose up -d postgres

    echo "Waiting for PostgreSQL to be ready..."
    sleep 5

    # Wait for PostgreSQL to be healthy
    until docker-compose exec -T postgres pg_isready -U noma > /dev/null 2>&1; do
        echo "   Waiting for database..."
        sleep 2
    done

    echo "[OK] PostgreSQL is ready"

    echo ""
    echo "Setting up database schema..."
    npm run db:push

    echo ""
    echo "Seeding database with sample data..."
    npm run db:seed
else
    echo ""
    echo "[WARNING] Docker not available. Please:"
    echo "   1. Install and configure PostgreSQL manually"
    echo "   2. Update DATABASE_URL in .env"
    echo "   3. Run: npm run db:push"
    echo "   4. Run: npm run db:seed"
fi

echo ""
echo "Setup complete."
echo ""
echo "Next steps:"
echo "   1. Edit .env with your Stripe API keys"
echo "   2. Run: npm run dev"
echo "   3. Open: http://localhost:3000"
echo ""
echo "Admin credentials (from seed):"
echo "   Email: admin@nomacardhouse.com"
echo "   Password: admin123"
echo ""
