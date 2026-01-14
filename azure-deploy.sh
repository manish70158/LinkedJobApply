#!/bin/bash
# Azure deployment script for LinkedIn Auto Job Applier

set -e

echo "========================================"
echo "LinkedIn Auto Job Applier - Azure Deploy"
echo "========================================"
echo ""

# Configuration
RESOURCE_GROUP="${RESOURCE_GROUP:-linkedin-bot-rg}"
LOCATION="${LOCATION:-eastus}"
ACR_NAME="${ACR_NAME:-linkedinbotacr$(date +%s)}"
IMAGE_NAME="linkedin-job-applier"
IMAGE_TAG="${IMAGE_TAG:-latest}"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "Error: Azure CLI is not installed."
    echo "Please install it from: https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi

# Login to Azure (if not already logged in)
echo "Checking Azure login status..."
az account show &> /dev/null || {
    echo "Please login to Azure..."
    az login
}

# Get subscription info
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)
echo "Using subscription: $SUBSCRIPTION_NAME ($SUBSCRIPTION_ID)"
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

# Get ACR credentials
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

echo "ACR Login Server: $ACR_LOGIN_SERVER"
echo ""

# Build and push Docker image to ACR
echo "Building Docker image..."
docker build -f Dockerfile.azure -t $IMAGE_NAME:$IMAGE_TAG .
echo "✓ Docker image built"
echo ""

echo "Tagging image for ACR..."
docker tag $IMAGE_NAME:$IMAGE_TAG $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG
echo "✓ Image tagged"
echo ""

echo "Logging into ACR..."
echo $ACR_PASSWORD | docker login $ACR_LOGIN_SERVER --username $ACR_USERNAME --password-stdin
echo "✓ Logged into ACR"
echo ""

echo "Pushing image to ACR..."
docker push $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG
echo "✓ Image pushed to ACR"
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
echo "Deploying infrastructure using Bicep..."
az deployment group create \
    --resource-group $RESOURCE_GROUP \
    --template-file azure-deploy.bicep \
    --parameters \
        namePrefix=linkedinbot \
        containerImage=$ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG \
        linkedinUsername=$LN_USERNAME \
        linkedinPassword=$LN_PASSWORD \
        geminiApiKey=$GEMINI_API_KEY \
        runMode=$RUN_MODE \
        cpuCores=2 \
        memoryInGb=4

echo "✓ Infrastructure deployed"
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
echo "Useful Commands"
echo "========================================"
echo "View logs:"
echo "  az container logs --resource-group $RESOURCE_GROUP --name $CONTAINER_GROUP_NAME"
echo ""
echo "View container status:"
echo "  az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_GROUP_NAME"
echo ""
echo "Download logs from Azure Storage:"
echo "  az storage blob download-batch -d ./downloaded-logs -s linkedin-bot-data --account-name $STORAGE_ACCOUNT"
echo ""
echo "Delete deployment:"
echo "  az group delete --name $RESOURCE_GROUP --yes"
echo ""
echo "✓ Deployment complete!"
