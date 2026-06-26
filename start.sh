#!/bin/bash

# AutoAds - Quick Start Script for macOS/Linux

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║          AutoAds - Advertisement Website               ║"
echo "║                  Starting Server...                    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed!"
    echo ""
    echo "Please download and install Node.js from:"
    echo "https://nodejs.org/"
    echo ""
    exit 1
fi

echo "✅ Node.js detected"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    echo "This may take a minute..."
    echo ""
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

echo ""
echo "✅ Dependencies installed"
echo ""

# Start the server
echo "🚀 Starting AutoAds Server..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Server is running on: http://localhost:3000"
echo ""
echo "📝 First time?"
echo "   1. Click \"Sign up here\" to create account"
echo "   2. Go to \"Post Ad\" to create your first ad"
echo "   3. Browse ads from other users"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

npm start
