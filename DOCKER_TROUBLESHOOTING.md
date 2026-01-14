# Docker Build Troubleshooting Guide

## Common Docker Build Errors and Solutions

### Error: "failed to resolve source metadata" or "403 Forbidden"

This error occurs when Docker cannot pull the base image from Docker Hub.

#### Solutions:

### 1. Check Docker Hub Status
```bash
# Check if Docker Hub is accessible
curl -I https://hub.docker.com
```

### 2. Try Different Base Images
```bash
# Option 1: Use full python image (larger but more stable)
docker build -f Dockerfile.azure.full -t linkedin-job-applier:azure-test .

# Option 2: Pull base image explicitly first
docker pull python:3.10
docker build -f Dockerfile.azure -t linkedin-job-applier:azure-test .

# Option 3: Use latest Python 3.10 slim
docker pull python:3.10-slim-bookworm
# Then update Dockerfile.azure to use: FROM python:3.10-slim-bookworm
```

### 3. Clear Docker Cache
```bash
# Remove all build cache
docker builder prune -a

# Then try building again
docker build -f Dockerfile.azure -t linkedin-job-applier:azure-test .
```

### 4. Login to Docker Hub
```bash
# Login (creates authentication)
docker login

# Then try building again
docker build -f Dockerfile.azure -t linkedin-job-applier:azure-test .
```

### 5. Use Alternative Registry
```bash
# Pull from Microsoft Container Registry instead
docker pull mcr.microsoft.com/mirror/docker/library/python:3.10-slim

# Update Dockerfile.azure first line to:
# FROM mcr.microsoft.com/mirror/docker/library/python:3.10-slim
```

### 6. Check Network/Proxy Settings
```bash
# If behind corporate proxy, configure Docker
# Edit ~/.docker/config.json or Docker Desktop settings
```

### 7. Restart Docker
```bash
# macOS/Windows: Restart Docker Desktop
# Linux:
sudo systemctl restart docker
```

## Quick Fix for Azure Deployment

If Docker build continues to fail locally, you can build directly in Azure:

### Option A: Use Azure Container Registry Build
```bash
# Login to Azure
az login

# Create ACR if not exists
az acr create --resource-group linkedin-bot-rg --name linkedinbotacr --sku Basic

# Build image in Azure (no local Docker needed)
az acr build \
    --registry linkedinbotacr \
    --image linkedin-job-applier:latest \
    --file Dockerfile.azure \
    .
```

### Option B: Use Pre-built Image
I can provide a GitHub Container Registry image that you can use directly:

```bash
# Update azure-deploy.bicep to use:
# containerImage: 'ghcr.io/godsscion/linkedin-job-applier:latest'
```

## Recommended Approach

1. **First**: Try clearing Docker cache and pulling base image explicitly
```bash
docker builder prune -a
docker pull python:3.10-slim
docker build -f Dockerfile.azure -t linkedin-job-applier:azure-test .
```

2. **If that fails**: Use the full Python image
```bash
docker build -f Dockerfile.azure.full -t linkedin-job-applier:azure-test .
```

3. **If still failing**: Build directly in Azure
```bash
az acr build --registry linkedinbotacr --image linkedin-job-applier:latest --file Dockerfile.azure .
```

## Test Local Build
```bash
# After successful build, test it
docker run -it --rm linkedin-job-applier:azure-test python --version
```

## Need Help?
If none of these work, please share:
1. Your Docker version: `docker --version`
2. Your OS: macOS/Windows/Linux
3. Any proxy/firewall settings
4. The complete error message
