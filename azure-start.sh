#!/bin/bash
set -e

echo "========================================="
echo "LinkedIn Auto Job Applier - Azure Startup"
echo "========================================="
echo "Starting at: $(date)"
echo ""

# Start virtual display for headless Chrome
echo "Starting virtual display..."
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
XVFB_PID=$!
echo "Virtual display started (PID: $XVFB_PID)"

# Wait for display to be ready
sleep 3

# Verify display is running
if ! ps -p $XVFB_PID > /dev/null; then
    echo "ERROR: Virtual display failed to start"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "========================================="
    echo "Shutting down services..."
    echo "========================================="
    kill $XVFB_PID 2>/dev/null || true
    
    # Upload logs to Azure Blob Storage if configured
    if [ ! -z "$AZURE_STORAGE_CONNECTION_STRING" ]; then
        echo "Uploading logs to Azure Storage..."
        python upload_logs_to_azure.py || echo "Warning: Failed to upload logs"
    fi
    
    echo "Cleanup complete. Exiting."
    exit
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM EXIT

# Show environment info (without secrets)
echo "Environment Configuration:"
echo "  Python version: $(python --version)"
echo "  Chrome version: $(google-chrome --version)"
echo "  DISPLAY: $DISPLAY"
echo "  Working directory: $(pwd)"
echo "  Running in Azure: $RUNNING_IN_AZURE"
echo ""

# Check if this is a scheduled run or continuous run
RUN_MODE=${RUN_MODE:-"single"}

if [ "$RUN_MODE" = "continuous" ]; then
    echo "Starting in CONTINUOUS mode with scheduler..."
    python scheduler.py
elif [ "$RUN_MODE" = "dashboard" ]; then
    echo "Starting Flask Dashboard only..."
    python app.py
else
    echo "Starting in SINGLE RUN mode..."
    python runAiBot.py
fi

echo ""
echo "========================================="
echo "Application completed at: $(date)"
echo "========================================="
