#!/bin/bash
# Quick deployment test script for Azure

set -e

echo "========================================"
echo "Azure Deployment Test"
echo "========================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install from: https://docs.docker.com/get-docker/"
    exit 1
fi
echo "✓ Docker is installed"

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install from: https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi
echo "✓ Azure CLI is installed"

# Check Azure login
if ! az account show &> /dev/null; then
    echo "❌ Not logged into Azure. Running 'az login'..."
    az login
fi
echo "✓ Logged into Azure"

# Get subscription info
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)
echo "✓ Using subscription: $SUBSCRIPTION_NAME"
echo ""

# Build Docker image locally for testing
echo "Building Docker image locally..."
docker build -f Dockerfile.azure -t linkedin-job-applier:test .

if [ $? -eq 0 ]; then
    echo "✓ Docker image built successfully"
else
    echo "❌ Docker build failed"
    exit 1
fi

echo ""
echo "========================================"
echo "✓ All prerequisites met!"
echo "========================================"
echo ""
echo "You're ready to deploy to Azure!"
echo ""
echo "Next steps:"
echo "1. Review configuration in azure-deploy.bicep"
echo "2. Run: ./azure-deploy.sh"
echo ""
echo "Or for manual deployment, see: AZURE_DEPLOYMENT.md"
