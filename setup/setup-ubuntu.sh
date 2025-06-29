#!/bin/bash

# Check for root privileges
if [ "$EUID" -ne 0 ]; then 
    echo "Please run this script with sudo privileges"
    exit 1
fi

# Install required packages
apt-get update
apt-get install -y wget unzip xvfb python3-pip python3-venv curl

# Clean up any existing Chrome/ChromeDriver installations
sudo rm -rf /usr/bin/google-chrome /usr/local/bin/chromedriver chrome-linux64* chromedriver-linux64*

# Get Chrome version
CHROME_VERSION=$(/opt/google/chrome/chrome --version 2>/dev/null || google-chrome --version 2>/dev/null || echo "")
if [ -z "$CHROME_VERSION" ]; then
    echo "Chrome not found. Installing Chrome..."
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
    apt-get update
    apt-get install -y google-chrome-stable
    CHROME_VERSION=$(google-chrome --version)
fi

# Extract major version
CHROME_MAJOR_VERSION=$(echo "$CHROME_VERSION" | grep -oP '(\d+)' | head -1)
echo "Detected Chrome version: $CHROME_VERSION (Major: $CHROME_MAJOR_VERSION)"

# Try to get matching ChromeDriver version
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_MAJOR_VERSION")

if [ -z "$CHROMEDRIVER_VERSION" ]; then
    echo "No exact match found for Chrome version $CHROME_MAJOR_VERSION, trying Chrome for Testing..."
    CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_$CHROME_MAJOR_VERSION")
fi

if [ -z "$CHROMEDRIVER_VERSION" ]; then
    echo "No Chrome for Testing version found, trying previous version..."
    PREV_VERSION=$((CHROME_MAJOR_VERSION-1))
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$PREV_VERSION")
fi

if [ -z "$CHROMEDRIVER_VERSION" ]; then
    echo "Failed to find compatible ChromeDriver version"
    exit 1
fi

echo "Installing ChromeDriver version: $CHROMEDRIVER_VERSION"

# Create temporary directory for downloads
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR" || exit 1

# Download and install ChromeDriver
wget -q "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
unzip -o chromedriver_linux64.zip
sudo cp -f chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Clean up
cd - || exit 1
rm -rf "$TEMP_DIR"

# Set up directories and permissions
mkdir -p ~/Downloads
chmod 777 ~/Downloads
mkdir -p logs/screenshots
chmod -R 777 logs

# Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo "Setup complete! The environment is ready to run the LinkedIn Auto Job Applier."