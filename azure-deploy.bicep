// Azure Bicep template for deploying LinkedIn Auto Job Applier
// Deploys: Container Instance, Storage Account, and Container Registry

@description('Location for all resources')
param location string = resourceGroup().location

@description('Name prefix for resources')
param namePrefix string = 'linkedin-bot'

@description('Container image to deploy')
param containerImage string = 'linkedin-job-applier:latest'

@description('LinkedIn Username')
@secure()
param linkedinUsername string

@description('LinkedIn Password')
@secure()
param linkedinPassword string

@description('Gemini API Key')
@secure()
param geminiApiKey string

@description('Run mode: single, continuous, or dashboard')
@allowed([
  'single'
  'continuous'
  'dashboard'
])
param runMode string = 'continuous'

@description('Schedule hours (for continuous mode)')
param scheduleHours int = 6

@description('CPU cores')
param cpuCores int = 2

@description('Memory in GB')
param memoryInGb int = 4

// Storage Account for persisting logs and results
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: '${namePrefix}storage${uniqueString(resourceGroup().id)}'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
  }
}

// Blob container for application data
resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
}

resource dataContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobService
  name: 'linkedin-bot-data'
  properties: {
    publicAccess: 'None'
  }
}

// Container Registry (optional - if you want to use ACR)
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: '${namePrefix}acr${uniqueString(resourceGroup().id)}'
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

// Container Instance Group
resource containerGroup 'Microsoft.ContainerInstance/containerGroups@2023-05-01' = {
  name: '${namePrefix}-container'
  location: location
  properties: {
    containers: [
      {
        name: 'linkedin-job-applier'
        properties: {
          image: containerImage
          resources: {
            requests: {
              cpu: cpuCores
              memoryInGB: memoryInGb
            }
          }
          environmentVariables: [
            {
              name: 'LN_USERNAME'
              secureValue: linkedinUsername
            }
            {
              name: 'LN_PASSWORD'
              secureValue: linkedinPassword
            }
            {
              name: 'GEMINI_API_KEY'
              secureValue: geminiApiKey
            }
            {
              name: 'AZURE_STORAGE_CONNECTION_STRING'
              secureValue: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=${environment().suffixes.storage}'
            }
            {
              name: 'AZURE_STORAGE_CONTAINER'
              value: 'linkedin-bot-data'
            }
            {
              name: 'RUN_MODE'
              value: runMode
            }
            {
              name: 'SCHEDULE_HOURS'
              value: string(scheduleHours)
            }
            {
              name: 'RUNNING_IN_AZURE'
              value: 'true'
            }
            {
              name: 'GITHUB_ACTIONS'
              value: 'true'
            }
          ]
          ports: runMode == 'dashboard' ? [
            {
              port: 5000
              protocol: 'TCP'
            }
          ] : []
        }
      }
    ]
    osType: 'Linux'
    restartPolicy: runMode == 'single' ? 'Never' : 'Always'
    ipAddress: runMode == 'dashboard' ? {
      type: 'Public'
      ports: [
        {
          port: 5000
          protocol: 'TCP'
        }
      ]
      dnsNameLabel: '${namePrefix}-dashboard'
    } : null
  }
}

// Outputs
output containerGroupId string = containerGroup.id
output containerGroupName string = containerGroup.name
output storageAccountName string = storageAccount.name
output containerRegistryLoginServer string = containerRegistry.properties.loginServer
output dashboardUrl string = runMode == 'dashboard' ? 'http://${containerGroup.properties.ipAddress.fqdn}:5000' : 'N/A'
