#!/bin/bash
# Direct deployment to Azure using ACR build (bypasses local Docker issues)

set -e

echo "========================================"
echo "Azure Direct Deploy (No Local Docker)"
echo "========================================"
echo ""

# Configuration
RESOURCE_GROUP="${RESOURCE_GROUP:-linkedin-bot-rg}"
LOCATION="${LOCATION:-eastus}"
ACR_NAME="linkedinbotacr$(date +%s | tail -c 6)"
IMAGE_NAME="linkedin-job-applier"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "Error: Azure CLI is not installed."
    echo "Please install it from: https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi

# Login to Azure
echo "Checking Azure login status..."
az account show &> /dev/null || {
    echo "Please login to Azure..."
    az login
}

SUBSCRIPTION_NAME=$(az account show --query name -o tsv)
echo "✓ Using subscription: $SUBSCRIPTION_NAME"
echo ""

# Create resource group
echo "Creating resource group: $RESOURCE_GROUP"
az group create --name $RESOURCE_GROUP --location $LOCATION
echo "✓ Resource group created"
echo ""

# Create Azure Container Registry
echo "Creating Azure Container Registry: $ACR_NAME"
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true
echo "✓ Container Registry created"
echo ""

# Build image directly in Azure (no local Docker required!)
echo "Building Docker image in Azure Container Registry..."
echo "This bypasses any local Docker issues!"
echo ""

az acr build \
    --registry $ACR_NAME \
    --resource-group $RESOURCE_GROUP \
    --image $IMAGE_NAME:latest \
    --file Dockerfile.azure \
    .

echo ""
echo "✓ Image built successfully in Azure!"
echo ""

# Get ACR details
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)
echo "ACR Login Server: $ACR_LOGIN_SERVER"
echo ""

# Prompt for secrets
echo "Please provide the following credentials:"
read -p "LinkedIn Username: " LN_USERNAME
read -sp "LinkedIn Password: " LN_PASSWORD
echo ""
read -sp "Gemini API Key: " GEMINI_API_KEY
echo ""
echo ""

# Choose deployment mode
echo "Select deployment mode:"
echo "1. Single Run (runs once and stops)"
echo "2. Continuous (scheduled runs every 6 hours)"
echo "3. Dashboard (Flask web interface only)"
read -p "Enter choice [1-3]: " DEPLOY_MODE

case $DEPLOY_MODE in
    1) RUN_MODE="single" ;;
    2) RUN_MODE="continuous" ;;
    3) RUN_MODE="dashboard" ;;
    *) RUN_MODE="continuous" ;;
esac

echo "Deployment mode: $RUN_MODE"
echo ""

# Deploy using Bicep
echo "Deploying infrastructure..."
az deployment group create \
    --resource-group $RESOURCE_GROUP \
    --template-file azure-deploy.bicep \
    --parameters \
        namePrefix=linkedinbot \
        containerImage=$ACR_LOGIN_SERVER/$IMAGE_NAME:latest \
        linkedinUsername="$LN_USERNAME" \
        linkedinPassword="$LN_PASSWORD" \
        geminiApiKey="$GEMINI_API_KEY" \
        runMode=$RUN_MODE

echo "✓ Deployment complete!"
echo ""

# Get outputs
CONTAINER_GROUP_NAME=$(az deployment group show \
    --resource-group $RESOURCE_GROUP \
    --name azure-deploy \
    --query properties.outputs.containerGroupName.value -o tsv)

STORAGE_ACCOUNT=$(az deployment group show \
    --resource-group $RESOURCE_GROUP \
    --name azure-deploy \
    --query properties.outputs.storageAccountName.value -o tsv)

echo "========================================"
echo "Deployment Summary"
echo "========================================"
echo "Resource Group: $RESOURCE_GROUP"
echo "Container Registry: $ACR_LOGIN_SERVER"
echo "Container Group: $CONTAINER_GROUP_NAME"
echo "Storage Account: $STORAGE_ACCOUNT"
echo "Run Mode: $RUN_MODE"

if [ "$RUN_MODE" = "dashboard" ]; then
    DASHBOARD_URL=$(az deployment group show \
        --resource-group $RESOURCE_GROUP \
        --name azure-deploy \
        --query properties.outputs.dashboardUrl.value -o tsv)
    echo "Dashboard URL: $DASHBOARD_URL"
fi

echo ""
echo "========================================"
echo "Monitor Your Deployment"
echo "========================================"
echo "View logs:"
echo "  az container logs --resource-group $RESOURCE_GROUP --name $CONTAINER_GROUP_NAME --follow"
echo ""
echo "✓ All done! Your bot is now running in Azure!"
