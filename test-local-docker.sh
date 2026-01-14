#!/bin/bash
# Local test script to verify the application works before Azure deployment

set -e

echo "========================================"
echo "Local Test Run"
echo "========================================"
echo ""

# Build Docker image
echo "Building Docker image..."
docker build -f Dockerfile.azure -t linkedin-job-applier:local-test .
echo "✓ Image built"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
# LinkedIn Credentials
LN_USERNAME=a.manish1689@gmail.com
LN_PASSWORD=Haryanao@123

# API Keys
GEMINI_API_KEY=AIzaSyBscr8qdwTKxJpI1UgVX2FEhLFypBu8vOw

# Azure Storage (optional for local testing)
AZURE_STORAGE_CONNECTION_STRING=

# Configuration
RUN_MODE=single
SCHEDULE_HOURS=6
RUNNING_IN_AZURE=false
GITHUB_ACTIONS=true
EOF
    echo "✓ .env file created. Please edit it with your credentials."
    echo ""
    read -p "Press Enter after updating .env file to continue..."
fi

# Load environment variables
source .env

# Run container locally
echo "Starting container locally..."
echo "Note: This runs in test mode with virtual display"
echo ""

docker run -it --rm \
    --name linkedin-bot-test \
    -e LN_USERNAME="$LN_USERNAME" \
    -e LN_PASSWORD="$LN_PASSWORD" \
    -e GEMINI_API_KEY="$GEMINI_API_KEY" \
    -e RUN_MODE="${RUN_MODE:-single}" \
    -e RUNNING_IN_AZURE=false \
    -e GITHUB_ACTIONS=true \
    -v "$(pwd)/logs:/app/logs" \
    -v "$(pwd)/all excels:/app/all excels" \
    linkedin-job-applier:local-test

echo ""
echo "========================================"
echo "Local test completed!"
echo "========================================"
echo "Check logs/ directory for output"
