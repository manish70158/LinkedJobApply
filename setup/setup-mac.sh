#!/bin/bash

# Exit on error
set -e

echo "Setting up LinkedIn Auto Job Applier for macOS..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew is already installed."
    brew update
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Installing Python 3..."
    brew install python
else
    echo "Python 3 is already installed."
fi

# Get Chrome version
if [ -f "/Applications/Google Chrome.app/Contents/Info.plist" ]; then
    CHROME_VERSION=$(defaults read /Applications/Google\ Chrome.app/Contents/Info.plist CFBundleShortVersionString | cut -d. -f1)
    echo "Chrome version detected: $CHROME_VERSION"
else
    echo "Installing Google Chrome..."
    brew install --cask google-chrome
    CHROME_VERSION=$(defaults read /Applications/Google\ Chrome.app/Contents/Info.plist CFBundleShortVersionString | cut -d. -f1)
fi

# Install ChromeDriver using Homebrew
echo "Installing ChromeDriver using Homebrew..."
brew install --cask chromedriver

# Verify ChromeDriver installation and set permissions
if [ -f "/usr/local/bin/chromedriver" ]; then
    echo "ChromeDriver installed successfully!"
    echo "Setting permissions..."
    chmod +x /usr/local/bin/chromedriver
    # Remove quarantine attribute that may block execution
    sudo xattr -d com.apple.quarantine /usr/local/bin/chromedriver || true
elif [ -f "/opt/homebrew/bin/chromedriver" ]; then
    echo "ChromeDriver installed successfully!"
    echo "Setting permissions..."
    chmod +x /opt/homebrew/bin/chromedriver
    # Remove quarantine attribute that may block execution
    sudo xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver || true
else
    echo "Error: ChromeDriver installation failed"
    exit 1
fi

# Create required directories
mkdir -p ~/Downloads logs/screenshots "all excels" "all resumes/temp"
chmod -R 755 ~/Downloads logs "all excels" "all resumes"

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install requirements
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "Setup complete! The environment is ready to run the LinkedIn Auto Job Applier."