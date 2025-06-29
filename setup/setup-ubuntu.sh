#!/bin/bash

# Check for root privileges
if [ "$EUID" -ne 0 ]; then 
    echo "Please run this script with sudo privileges"
    exit 1
fi

# Install required packages
apt-get update
apt-get install -y wget unzip xvfb python3-pip python3-venv

# Clean up any existing Chrome/ChromeDriver installations
sudo rm -rf /usr/bin/google-chrome /usr/local/bin/chromedriver chrome-linux64* chromedriver-linux64*

# Get latest Chrome and ChromeDriver versions
CHROME_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE)
echo "Latest Chrome version: $CHROME_VERSION"

# Create temporary directory for downloads
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR" || exit 1

# Download and install Chrome for Testing
wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROME_VERSION/linux64/chrome-linux64.zip"
yes | unzip -o chrome-linux64.zip
sudo cp -f chrome-linux64/chrome /usr/bin/google-chrome
sudo chmod +x /usr/bin/google-chrome

# Download and install matching ChromeDriver
wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROME_VERSION/linux64/chromedriver-linux64.zip"
yes | unzip -o chromedriver-linux64.zip
sudo cp -f chromedriver-linux64/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Clean up temporary directory
cd - || exit 1
rm -rf "$TEMP_DIR"

# Set up directories and permissions
mkdir -p ~/Downloads
chmod 777 ~/Downloads
mkdir -p logs/screenshots
chmod -R 777 logs

# Set up virtual display for headless mode
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
sleep 3

# Print versions for debugging
echo "Chrome version:"
google-chrome --version || true
echo "ChromeDriver version:"
chromedriver --version || true

# Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo "Setup complete! The environment is ready to run the LinkedIn Auto Job Applier."