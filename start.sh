#!/bin/bash

# Start script for Secure P2P Chat

echo "🔐 Secure P2P Chat - Starting..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if dependencies are installed
echo "📦 Checking dependencies..."
python3 -c "import nacl, websockets, customtkinter" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "⚠️  Dependencies not found. Installing..."
    pip install -r requirements.txt

    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies. Please run: pip install -r requirements.txt"
        exit 1
    fi
fi

echo "✅ Dependencies OK"
echo ""
echo "🚀 Launching application..."
echo ""

# Run the application
python3 gui.py
