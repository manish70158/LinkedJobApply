#!/bin/bash

# Check for root privileges
if [ "$EUID" -ne 0 ]; then 
    echo "Please run this script with sudo privileges"
    exit 1
fi

# Install required packages
apt-get update
apt-get install -y wget unzip xvfb python3-pip python3-venv curl x11-utils scrot python3-tk python3-dev

# Remove any existing Chrome installations
apt-get remove -y google-chrome-stable
rm -rf /etc/apt/sources.list.d/google-chrome*.list /usr/local/bin/chromedriver ~/.local/bin/chromedriver

# Install Chrome
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
apt-get update
apt-get install -y google-chrome-stable

# Get Chrome version
CHROME_VERSION=$(google-chrome --version | grep -oP '(?<=Google Chrome )\d+\.\d+\.\d+\.\d+')
CHROME_MAJOR_VERSION=$(echo "$CHROME_VERSION" | cut -d. -f1)
echo "Detected Chrome version: $CHROME_VERSION (Major: $CHROME_MAJOR_VERSION)"

# Try Chrome for Testing first (newer approach)
echo "Trying Chrome for Testing version..."
CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_$CHROME_MAJOR_VERSION")
IS_CHROME_FOR_TESTING=true

if [ -z "$CHROMEDRIVER_VERSION" ]; then
    echo "No Chrome for Testing version found, trying legacy ChromeDriver..."
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_MAJOR_VERSION")
    IS_CHROME_FOR_TESTING=false
fi

if [ -z "$CHROMEDRIVER_VERSION" ]; then
    echo "No exact match found, trying previous Chrome version..."
    PREV_VERSION=$((CHROME_MAJOR_VERSION-1))
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$PREV_VERSION")
    IS_CHROME_FOR_TESTING=false
fi

if [ -z "$CHROMEDRIVER_VERSION" ]; then
    echo "Failed to find compatible ChromeDriver version"
    exit 1
fi

echo "Installing ChromeDriver version: $CHROMEDRIVER_VERSION"

# Create directories for ChromeDriver
mkdir -p /usr/local/bin ~/.local/bin

# Download and install ChromeDriver
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR" || exit 1

if [ "$IS_CHROME_FOR_TESTING" = true ]; then
    echo "Downloading Chrome for Testing ChromeDriver..."
    wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip"
    unzip -o chromedriver-linux64.zip
    cp -f chromedriver-linux64/chromedriver /usr/local/bin/
    cp -f chromedriver-linux64/chromedriver ~/.local/bin/
else
    echo "Downloading legacy ChromeDriver..."
    wget -q "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
    unzip -o chromedriver_linux64.zip
    cp -f chromedriver /usr/local/bin/
    cp -f chromedriver ~/.local/bin/
fi

# Set permissions
chmod +x /usr/local/bin/chromedriver
chmod +x ~/.local/bin/chromedriver

# Clean up
cd - || exit 1
rm -rf "$TEMP_DIR"

# Set up project directories
mkdir -p ~/Downloads logs/screenshots "all excels" "all resumes/temp"
chmod -R 777 ~/Downloads logs "all excels" "all resumes"

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install system dependencies for PyAutoGUI
apt-get install -y python3-tk python3-dev scrot

# Upgrade pip and install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Set up virtual display
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
sleep 3

# Print versions for verification
echo "Chrome version:"
google-chrome --version
echo "ChromeDriver version:"
chromedriver --version
echo "Python version:"
python3 --version
echo "Display: $DISPLAY"
echo "ChromeDriver location: $(which chromedriver)"
echo "Chrome binary location: $(which google-chrome)"

echo "Setup complete! The environment is ready to run the LinkedIn Auto Job Applier."