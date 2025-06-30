#!/bin/bash

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Installing pip..."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py --user
    rm get-pip.py
fi

# Install Homebrew if not installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew is not installed. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install Chrome if not present (using Homebrew)
if ! [ -d "/Applications/Google Chrome.app" ]; then
    echo "Installing Google Chrome..."
    brew install --cask google-chrome
fi

# Get Chrome version
CHROME_VERSION=$(defaults read /Applications/Google\ Chrome.app/Contents/Info.plist CFBundleShortVersionString | cut -d. -f1)
echo "Chrome version detected: $CHROME_VERSION"

# Install ChromeDriver using Homebrew
echo "Installing ChromeDriver using Homebrew..."
brew install --cask chromedriver

# Verify ChromeDriver installation
if [ -f "/opt/homebrew/bin/chromedriver" ]; then
    echo "ChromeDriver installed successfully!"
    echo "Setting permissions..."
    chmod +x /opt/homebrew/bin/chromedriver
else
    echo "Error: ChromeDriver installation failed"
    exit 1
fi

# Create required directories
mkdir -p ~/Downloads
chmod 755 ~/Downloads

# Set up Python environment and install requirements
python3 -m pip install --upgrade pip
python3 -m pip install -r ../requirements.txt

echo "Setup complete! The environment is ready to run the LinkedIn Auto Job Applier."