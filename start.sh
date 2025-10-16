#!/bin/bash

# Fantasy Basketball Oracle - Quick Start Script
# This script helps you get started quickly

echo "🏀 Fantasy Basketball Oracle - Quick Start"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating environment file..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env with your Yahoo API credentials"
    echo "   You can get credentials from: https://developer.yahoo.com/apps/"
    echo ""
    read -p "Press Enter when you've added your credentials..."
fi

echo "🚀 Starting Fantasy Basketball Oracle..."
echo ""

# Build and start containers
docker-compose up --build

echo ""
echo "✅ Application started!"
echo ""
echo "Access your assistant at:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
