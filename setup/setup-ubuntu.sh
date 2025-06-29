#!/bin/bash

# Check for root privileges
if [ "$EUID" -ne 0 ]; then 
    echo "Please run this script with sudo privileges"
    exit 1
fi

# Install required packages
apt-get update
apt-get install -y wget unzip xvfb python3-pip python3-venv curl

# Install Chrome if not present
if ! command -v google-chrome &> /dev/null; then
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
    apt-get update
    apt-get install -y google-chrome-stable
fi

# Get Chrome version
CHROME_VERSION=$(google-chrome --version | grep -oP '(\d+\.\d+\.\d+\.\d+)')
CHROME_MAJOR_VERSION=$(echo "$CHROME_VERSION" | cut -d. -f1)
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

# Clean up any existing ChromeDriver installations
sudo rm -rf /usr/local/bin/chromedriver

# Download and install ChromeDriver
wget -q "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
unzip -o chromedriver_linux64.zip
sudo cp -f chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Clean up temporary files
cd - || exit 1
rm -rf "$TEMP_DIR"

# Set up directories and permissions
mkdir -p ~/Downloads
chmod 777 ~/Downloads
mkdir -p logs/screenshots
chmod -R 777 logs

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Print versions for verification
echo "Chrome version:"
google-chrome --version
echo "ChromeDriver version:"
chromedriver --version

echo "Setup complete! The environment is ready to run the LinkedIn Auto Job Applier."