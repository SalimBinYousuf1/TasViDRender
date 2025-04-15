#!/bin/bash

# TasVID Deployment Script
# This script helps deploy TasVID YouTube downloader application

echo "Starting TasVID deployment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip is not installed. Please install pip."
    exit 1
fi

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "ffmpeg is not installed. Please install ffmpeg."
    echo "On Ubuntu/Debian: sudo apt install ffmpeg"
    echo "On macOS: brew install ffmpeg"
    echo "On Windows: download from https://ffmpeg.org/download.html"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create downloads directory
mkdir -p downloads

# Start the application
echo "Starting TasVID application..."
echo "The application will be available at http://localhost:5000"
gunicorn --bind 0.0.0.0:5000 app:app

# Note: Press Ctrl+C to stop the application
