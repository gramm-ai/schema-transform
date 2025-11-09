#!/bin/bash

# Multi-Tenant Schema Translator - Quick Start Script
# This script helps set up and run the demo locally

echo "🚀 Multi-Tenant Schema Translator - Quick Start"
echo "=========================================="

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "❌ Python 3.9+ is required. Found: $python_version"
    exit 1
fi
echo "✅ Python $python_version found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependencies installed"

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.template .env
    echo "✅ .env file created"
    echo ""
    echo "📝 Please edit .env file with your Azure credentials:"
    echo "   - AZURE_OPENAI_API_KEY"
    echo "   - AZURE_OPENAI_ENDPOINT"
    echo "   - AZURE_SQL_SERVER (optional for mock data demo)"
    echo ""
    read -p "Press Enter after updating .env file to continue..."
fi

# Option to use Docker
echo ""
echo "Select run mode:"
echo "1. Run with mock data (no database required)"
echo "2. Run with Docker (includes SQL Server)"
echo "3. Run with Azure SQL Database"
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "Starting with mock data..."
        echo "✅ Server starting at http://localhost:8000"
        echo "🌐 Open http://localhost:8000/static/index.html in your browser"
        echo ""
        uvicorn app.main:app --reload --port 8000
        ;;
    2)
        echo "Starting with Docker..."
        if ! command -v docker &> /dev/null; then
            echo "❌ Docker is not installed. Please install Docker first."
            exit 1
        fi
        docker-compose up --build
        ;;
    3)
        echo "Starting with Azure SQL Database..."
        echo "Make sure your Azure SQL Database is configured and .env is updated"
        echo "✅ Server starting at http://localhost:8000"
        echo "🌐 Open http://localhost:8000/static/index.html in your browser"
        echo ""
        uvicorn app.main:app --reload --port 8000
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
