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

# Get Chrome version and download matching ChromeDriver
CHROME_VERSION=$(/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version | awk '{print $3}' | awk -F'.' '{print $1}')
echo "Chrome version detected: $CHROME_VERSION"

# Try to get matching ChromeDriver version
CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_$CHROME_VERSION")

if [ -z "$CHROMEDRIVER_VERSION" ]; then
    echo "No exact match found for Chrome version $CHROME_VERSION, trying previous version..."
    CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_$(($CHROME_VERSION-1))")
fi

if [ -z "$CHROMEDRIVER_VERSION" ]; then
    echo "Failed to find compatible ChromeDriver version"
    exit 1
fi

echo "Installing ChromeDriver version: $CHROMEDRIVER_VERSION"

# Determine Mac architecture and set platform
if [ "$(uname -m)" = "arm64" ]; then
    PLATFORM="mac_arm64"
else
    PLATFORM="mac64"
fi

# Create local bin directory if it doesn't exist
mkdir -p ~/.local/bin

# Download and install ChromeDriver
echo "Downloading ChromeDriver for $PLATFORM..."
curl -Lo chromedriver.zip "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROMEDRIVER_VERSION/$PLATFORM/chromedriver-$PLATFORM.zip"
unzip -o chromedriver.zip
mv chromedriver-$PLATFORM/chromedriver ~/.local/bin/
chmod +x ~/.local/bin/chromedriver
rm -rf chromedriver.zip chromedriver-$PLATFORM

# Add ~/.local/bin to PATH if not already there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    export PATH="$HOME/.local/bin:$PATH"
fi

# Create required directories
mkdir -p ~/Downloads
chmod 755 ~/Downloads

# Set up Python environment and install requirements
python3 -m pip install --upgrade pip
python3 -m pip install -r ../requirements.txt

echo "Setup complete! The environment is ready to run the LinkedIn Auto Job Applier."