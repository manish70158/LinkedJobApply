#!/bin/bash

# Check for root privileges
if [ "$EUID" -ne 0 ]; then 
    echo "Please run this script with sudo privileges"
    exit 1
fi

# Install required packages
apt-get update
apt-get install -y wget unzip xvfb python3-pip python3-venv

# Install Chrome if not present
if ! command -v google-chrome &> /dev/null; then
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
    apt-get update
    apt-get install -y google-chrome-stable
fi

# Get Chrome version and download matching ChromeDriver
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | awk -F'.' '{print $1}')
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

# Clean up any existing ChromeDriver files
rm -rf chromedriver-linux64 chromedriver-linux64.zip /usr/local/bin/chromedriver

# Download and install ChromeDriver
wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip"

# Create a temporary directory for extraction
TEMP_DIR=$(mktemp -d)
unzip -q chromedriver-linux64.zip -d "$TEMP_DIR"

# Move ChromeDriver to final location
mv "$TEMP_DIR/chromedriver-linux64/chromedriver" /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

# Clean up
rm -rf "$TEMP_DIR" chromedriver-linux64.zip

# Create required directories with proper permissions
mkdir -p ~/Downloads
chmod 777 ~/Downloads

# Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete! The environment is ready to run the LinkedIn Auto Job Applier."