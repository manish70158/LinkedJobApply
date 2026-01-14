# Azure Deployment Guide for LinkedIn Auto Job Applier

This guide will help you deploy the LinkedIn Auto Job Applier to Azure Container Instances with persistent storage.

## 📋 Prerequisites

1. **Azure Account**: Active Azure subscription ([Create free account](https://azure.microsoft.com/free/))
2. **Azure CLI**: Install from [here](https://docs.microsoft.com/cli/azure/install-azure-cli)
3. **Docker**: Install from [here](https://docs.docker.com/get-docker/)
4. **Git**: For cloning the repository

## 🏗️ Architecture

The deployment includes:
- **Azure Container Instances (ACI)**: Runs the bot in containers
- **Azure Container Registry (ACR)**: Stores Docker images
- **Azure Storage Account**: Persists logs and application data
- **Blob Storage**: Stores results and execution history

## 🚀 Quick Start Deployment

### Option 1: Automated Script (Recommended)

```bash
# Make the script executable
chmod +x azure-deploy.sh

# Run the deployment script
./azure-deploy.sh
```

The script will:
1. Login to Azure
2. Create a resource group
3. Create Azure Container Registry
4. Build and push Docker image
5. Deploy container instance
6. Set up persistent storage

### Option 2: Manual Deployment

#### Step 1: Login to Azure

```bash
az login
```

#### Step 2: Set Variables

```bash
export RESOURCE_GROUP="linkedin-bot-rg"
export LOCATION="eastus"
export ACR_NAME="linkedinbotacr$(date +%s)"
export IMAGE_NAME="linkedin-job-applier"
```

#### Step 3: Create Resource Group

```bash
az group create --name $RESOURCE_GROUP --location $LOCATION
```

#### Step 4: Create Container Registry

```bash
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true
```

#### Step 5: Build and Push Docker Image

```bash
# Login to ACR
az acr login --name $ACR_NAME

# Build the image
docker build -f Dockerfile.azure -t $IMAGE_NAME:latest .

# Tag for ACR
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)
docker tag $IMAGE_NAME:latest $ACR_LOGIN_SERVER/$IMAGE_NAME:latest

# Push to ACR
docker push $ACR_LOGIN_SERVER/$IMAGE_NAME:latest
```

#### Step 6: Deploy Using Bicep

```bash
az deployment group create \
    --resource-group $RESOURCE_GROUP \
    --template-file azure-deploy.bicep \
    --parameters \
        containerImage=$ACR_LOGIN_SERVER/$IMAGE_NAME:latest \
        linkedinUsername="YOUR_LINKEDIN_EMAIL" \
        linkedinPassword="YOUR_LINKEDIN_PASSWORD" \
        geminiApiKey="YOUR_GEMINI_API_KEY" \
        runMode="continuous"
```

## ⚙️ Configuration

### Run Modes

1. **Single Run** (`runMode=single`): Runs once and stops
2. **Continuous** (`runMode=continuous`): Scheduled runs every 6 hours
3. **Dashboard** (`runMode=dashboard`): Flask web interface only

### Environment Variables

Configure these in the Azure Container Instance:

| Variable | Description | Required |
|----------|-------------|----------|
| `LN_USERNAME` | LinkedIn email | Yes |
| `LN_PASSWORD` | LinkedIn password | Yes |
| `GEMINI_API_KEY` | Gemini API key for AI | Yes (if using AI) |
| `SCHEDULE_HOURS` | Hours between runs | No (default: 6) |
| `RUN_MODE` | single/continuous/dashboard | No (default: continuous) |
| `AZURE_STORAGE_CONNECTION_STRING` | Auto-configured | Auto |

## 📊 Monitoring & Logs

### View Container Logs

```bash
# Real-time logs
az container logs --resource-group $RESOURCE_GROUP --name linkedinbot-container --follow

# Last 100 lines
az container logs --resource-group $RESOURCE_GROUP --name linkedinbot-container --tail 100
```

### View Container Status

```bash
az container show \
    --resource-group $RESOURCE_GROUP \
    --name linkedinbot-container \
    --query instanceView.state
```

### Download Logs from Azure Storage

```bash
# Get storage account name
STORAGE_ACCOUNT=$(az deployment group show \
    --resource-group $RESOURCE_GROUP \
    --name azure-deploy \
    --query properties.outputs.storageAccountName.value -o tsv)

# Download all logs
az storage blob download-batch \
    -d ./downloaded-logs \
    -s linkedin-bot-data \
    --account-name $STORAGE_ACCOUNT
```

## 🔄 Update Deployment

### Rebuild and Redeploy

```bash
# Build new image
docker build -f Dockerfile.azure -t $ACR_LOGIN_SERVER/$IMAGE_NAME:latest .

# Push to ACR
docker push $ACR_LOGIN_SERVER/$IMAGE_NAME:latest

# Restart container (pulls latest image)
az container restart \
    --resource-group $RESOURCE_GROUP \
    --name linkedinbot-container
```

## 💰 Cost Estimation

Approximate monthly costs (East US region):

| Service | Configuration | Est. Monthly Cost |
|---------|--------------|-------------------|
| Container Instance | 2 CPU, 4GB RAM, continuous | ~$60-80 |
| Container Registry | Basic | ~$5 |
| Storage Account | Standard LRS, 10GB | ~$0.20 |
| **Total** | | **~$65-85** |

For **single runs** (on-demand):
- Only pay when running (~$0.10/hour)
- Could be ~$5-10/month if run a few times daily

## 🔒 Security Best Practices

1. **Use Azure Key Vault** for secrets:
```bash
# Create Key Vault
az keyvault create \
    --name linkedinbot-keyvault \
    --resource-group $RESOURCE_GROUP

# Store secrets
az keyvault secret set --vault-name linkedinbot-keyvault --name LnUsername --value "YOUR_EMAIL"
az keyvault secret set --vault-name linkedinbot-keyvault --name LnPassword --value "YOUR_PASSWORD"
```

2. **Enable Managed Identity** for the container
3. **Use Private Container Registry** (ACR with private endpoints)
4. **Enable Azure Monitor** for logging and alerts

## 🔧 Troubleshooting

### Container Won't Start

```bash
# Check container events
az container show \
    --resource-group $RESOURCE_GROUP \
    --name linkedinbot-container \
    --query instanceView.events

# Check container logs
az container logs --resource-group $RESOURCE_GROUP --name linkedinbot-container
```

### Chrome Issues

The Dockerfile includes:
- Xvfb for virtual display
- Latest Chrome stable version
- All required dependencies

### Storage Issues

```bash
# Verify storage account
az storage account show --name $STORAGE_ACCOUNT

# List containers
az storage container list --account-name $STORAGE_ACCOUNT
```

## 🗑️ Cleanup

### Delete Everything

```bash
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

### Delete Specific Resources

```bash
# Delete container only
az container delete --resource-group $RESOURCE_GROUP --name linkedinbot-container --yes

# Delete ACR only
az acr delete --name $ACR_NAME --yes
```

## 🤖 GitHub Actions Deployment

For automated deployments using GitHub Actions:

1. **Create Azure Service Principal**:
```bash
az ad sp create-for-rbac \
    --name "github-actions-linkedin-bot" \
    --role contributor \
    --scopes /subscriptions/{subscription-id}/resourceGroups/$RESOURCE_GROUP \
    --sdk-auth
```

2. **Add GitHub Secrets**:
   - `AZURE_CREDENTIALS`: Output from above command
   - `LN_USERNAME`: Your LinkedIn email
   - `LN_PASSWORD`: Your LinkedIn password
   - `GEMINI_API_KEY`: Your Gemini API key

3. **Trigger Deployment**:
   - Go to Actions tab in GitHub
   - Select "Deploy to Azure" workflow
   - Click "Run workflow"

## 📚 Additional Resources

- [Azure Container Instances Documentation](https://docs.microsoft.com/azure/container-instances/)
- [Azure Container Registry Documentation](https://docs.microsoft.com/azure/container-registry/)
- [Azure Bicep Documentation](https://docs.microsoft.com/azure/azure-resource-manager/bicep/)
- [Project GitHub Repository](https://github.com/GodsScion/Auto_job_applier_linkedIn)

## 🆘 Support

For issues and questions:
- GitHub Issues: [Project Issues](https://github.com/GodsScion/Auto_job_applier_linkedIn/issues)
- Discord: [Join Server](https://discord.gg/fFp7uUzWCY)

---

**Note**: Always test in a development environment before deploying to production. Monitor costs and usage regularly.
