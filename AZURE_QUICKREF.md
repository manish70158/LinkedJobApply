# Azure Deployment Quick Reference

## 🚀 Quick Deploy Commands

### 1. One-Command Deployment
```bash
./azure-deploy.sh
```

### 2. Test Before Deployment
```bash
# Check prerequisites
./test-azure-setup.sh

# Test Docker image locally
./test-local-docker.sh
```

## 📋 Common Azure CLI Commands

### Deployment Management
```bash
# View logs in real-time
az container logs --resource-group linkedin-bot-rg --name linkedinbot-container --follow

# Check container status
az container show --resource-group linkedin-bot-rg --name linkedinbot-container --query instanceView.state

# Restart container
az container restart --resource-group linkedin-bot-rg --name linkedinbot-container

# Delete container (keeps data)
az container delete --resource-group linkedin-bot-rg --name linkedinbot-container --yes
```

### Storage Management
```bash
# List storage accounts
az storage account list --resource-group linkedin-bot-rg --output table

# Download logs from storage
STORAGE_ACCOUNT=$(az storage account list --resource-group linkedin-bot-rg --query [0].name -o tsv)
az storage blob download-batch -d ./logs -s linkedin-bot-data --account-name $STORAGE_ACCOUNT

# List all files in storage
az storage blob list -c linkedin-bot-data --account-name $STORAGE_ACCOUNT --output table
```

### Cost Management
```bash
# View current costs
az consumption usage list --start-date 2026-01-01 --end-date 2026-01-31

# Set budget alert
az consumption budget create \
    --resource-group linkedin-bot-rg \
    --budget-name linkedin-bot-budget \
    --amount 100 \
    --time-grain Monthly
```

### Monitoring
```bash
# Get container metrics
az monitor metrics list \
    --resource /subscriptions/{subscription-id}/resourceGroups/linkedin-bot-rg/providers/Microsoft.ContainerInstance/containerGroups/linkedinbot-container \
    --metric CPUUsage

# View container events
az container show \
    --resource-group linkedin-bot-rg \
    --name linkedinbot-container \
    --query instanceView.events
```

## 🔧 Configuration Updates

### Update Environment Variables
```bash
# Get current container configuration
az container show --resource-group linkedin-bot-rg --name linkedinbot-container > container-config.json

# Edit the JSON file to update environment variables
# Then redeploy using the updated bicep template
```

### Change Run Mode
```bash
# Update to continuous mode
az deployment group create \
    --resource-group linkedin-bot-rg \
    --template-file azure-deploy.bicep \
    --parameters runMode=continuous

# Update to dashboard mode
az deployment group create \
    --resource-group linkedin-bot-rg \
    --template-file azure-deploy.bicep \
    --parameters runMode=dashboard
```

## 🔒 Security Commands

### Rotate Credentials
```bash
# Update LinkedIn password
az container exec \
    --resource-group linkedin-bot-rg \
    --name linkedinbot-container \
    --exec-command "env LN_PASSWORD='new_password'"

# Or redeploy with new credentials
```

### Access Container Registry
```bash
# Get ACR credentials
az acr credential show --name linkedinbotacr

# Login to ACR
az acr login --name linkedinbotacr
```

## 🗑️ Cleanup Commands

### Delete Everything
```bash
# Nuclear option - deletes all resources
az group delete --name linkedin-bot-rg --yes --no-wait
```

### Selective Cleanup
```bash
# Keep storage, delete container
az container delete --resource-group linkedin-bot-rg --name linkedinbot-container --yes

# Delete old container images
az acr repository delete --name linkedinbotacr --repository linkedin-job-applier --yes
```

## 💡 Tips

1. **Save money**: Use `runMode=single` and trigger manually when needed
2. **Monitor costs**: Check Azure portal regularly
3. **Backup data**: Download logs from Azure Storage periodically
4. **Test locally**: Always test Docker image locally before deploying
5. **Use Key Vault**: Store secrets in Azure Key Vault for production

## 🆘 Troubleshooting

### Container won't start
```bash
# Check events
az container show --resource-group linkedin-bot-rg --name linkedinbot-container --query instanceView.events

# Check logs
az container logs --resource-group linkedin-bot-rg --name linkedinbot-container
```

### Chrome issues
- Virtual display (Xvfb) should start automatically
- Check logs for "Starting virtual display" message
- Verify Chrome version in container

### Storage issues
```bash
# Verify storage connection
az storage account show-connection-string --name $STORAGE_ACCOUNT
```

## 📊 Cost Optimization

### Reduce Costs
1. Use smaller container size (1 CPU, 2GB RAM for testing)
2. Use `runMode=single` instead of continuous
3. Schedule runs during off-peak hours
4. Delete container when not in use (data persists in storage)

### Monitor Costs
```bash
# Current month costs
az consumption usage list \
    --start-date $(date -d "first day of this month" +%Y-%m-%d) \
    --output table
```

---

**For full documentation, see:** [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md)
