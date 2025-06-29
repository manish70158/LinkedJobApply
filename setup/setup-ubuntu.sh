#!/bin/bash

# Check for root privileges
if [ "$EUID" -ne 0 ]; then 
    echo "Please run this script with sudo privileges"
    exit 1
fi

# Install required packages
apt-get update
apt-get install -y wget unzip xvfb python3-pip python3-venv curl x11-utils scrot

# Remove any existing Chrome installations
apt-get remove -y google-chrome-stable
rm -rf /etc/apt/sources.list.d/google-chrome*.list

# Install Chrome
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
apt-get update
apt-get install -y google-chrome-stable

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
sudo rm -rf /usr/local/bin/chromedriver ~/.local/bin/chromedriver

# Download and install ChromeDriver
wget -q "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
unzip -o chromedriver_linux64.zip

# Install ChromeDriver in both system and user locations for compatibility
sudo cp -f chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

mkdir -p ~/.local/bin
cp -f chromedriver ~/.local/bin/
chmod +x ~/.local/bin/chromedriver

# Add ~/.local/bin to PATH if not already present
if ! grep -q "export PATH=\$HOME/.local/bin:\$PATH" ~/.bashrc; then
    echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
fi

# Clean up temporary files
cd - || exit 1
rm -rf "$TEMP_DIR"

# Set up directories and permissions
mkdir -p ~/Downloads
chmod 777 ~/Downloads

# Set up project directories
mkdir -p logs/screenshots
chmod -R 777 logs
mkdir -p "all excels"
chmod -R 777 "all excels"
mkdir -p "all resumes/temp"
chmod -R 777 "all resumes"

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install system dependencies for PyAutoGUI
apt-get install -y python3-tk python3-dev scrot

# Upgrade pip and install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Set up virtual display for headless mode
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
sleep 3

# Print versions for verification
echo "Chrome version:"
google-chrome --version
echo "ChromeDriver version:"
chromedriver --version

# Print environment info
echo "Display: $DISPLAY"
echo "ChromeDriver path: $(which chromedriver)"
echo "Python version: $(python3 --version)"

echo "Setup complete! The environment is ready to run the LinkedIn Auto Job Applier."