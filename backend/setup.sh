#!/bin/bash
# FutureBot Backend Setup Script

set -e  # Exit on error

echo "🤖 FutureBot Backend Setup"
echo "=========================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your Bybit API credentials!"
else
    echo "✓ .env file already exists"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs data/raw data/processed models

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Bybit API credentials"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run the application: uvicorn app.main:app --reload"
echo ""
