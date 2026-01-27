#!/bin/bash
# Setup script for Ollama and AI models

set -e

echo "=================================="
echo "Ollama Setup for AI Content Processing"
echo "=================================="
echo ""

# Check if Ollama is installed
if command -v ollama &> /dev/null; then
    echo "✓ Ollama is already installed"
    ollama --version
else
    echo "✗ Ollama is not installed"
    echo ""
    echo "Installing Ollama..."
    
    # Detect OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install ollama
        else
            echo "Please install Homebrew first: https://brew.sh"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -fsSL https://ollama.com/install.sh | sh
    else
        echo "Unsupported OS. Please install Ollama manually from: https://ollama.com/download"
        exit 1
    fi
fi

echo ""
echo "=================================="
echo "Starting Ollama Service"
echo "=================================="
echo ""

# Check if Ollama service is running
if pgrep -x "ollama" > /dev/null; then
    echo "✓ Ollama service is already running"
else
    echo "Starting Ollama service in background..."
    ollama serve &
    sleep 3
    echo "✓ Ollama service started"
fi

echo ""
echo "=================================="
echo "Downloading AI Models"
echo "=================================="
echo ""

# Function to check if model exists
model_exists() {
    ollama list | grep -q "$1"
}

# Recommended model for AI content processing
RECOMMENDED_MODEL="qwen2.5:latest"

echo "Recommended model: $RECOMMENDED_MODEL (excellent for Chinese/English content)"
echo ""

if model_exists "$RECOMMENDED_MODEL"; then
    echo "✓ $RECOMMENDED_MODEL is already downloaded"
else
    echo "Downloading $RECOMMENDED_MODEL (this may take a few minutes)..."
    ollama pull "$RECOMMENDED_MODEL"
    echo "✓ $RECOMMENDED_MODEL downloaded successfully"
fi

echo ""
echo "Would you like to download additional models? (y/n)"
read -r DOWNLOAD_MORE

if [[ "$DOWNLOAD_MORE" == "y" ]]; then
    echo ""
    echo "Additional Models:"
    echo "1. llama3.2:latest (Good for English)"
    echo "2. gemma2:latest (Lightweight and fast)"
    echo "3. mistral:latest (Multilingual support)"
    echo "4. All of the above"
    echo "5. Skip"
    echo ""
    echo "Enter your choice (1-5):"
    read -r CHOICE
    
    case $CHOICE in
        1)
            ollama pull llama3.2:latest
            ;;
        2)
            ollama pull gemma2:latest
            ;;
        3)
            ollama pull mistral:latest
            ;;
        4)
            ollama pull llama3.2:latest
            ollama pull gemma2:latest
            ollama pull mistral:latest
            ;;
        5)
            echo "Skipping additional models"
            ;;
        *)
            echo "Invalid choice, skipping"
            ;;
    esac
fi

echo ""
echo "=================================="
echo "Installed Models"
echo "=================================="
echo ""
ollama list

echo ""
echo "=================================="
echo "✓ Setup Complete!"
echo "=================================="
echo ""
echo "You can now use AI content processing in CMAS."
echo ""
echo "Test Ollama:"
echo "  curl http://localhost:11434/api/tags"
echo ""
echo "To use in CMAS:"
echo "1. Create a new event"
echo "2. Enable 'AI Content Processing' module"
echo "3. Select '$RECOMMENDED_MODEL' as AI model"
echo "4. Run the workflow after uploading a video"
echo ""
