"""
Script to upload logs and results to Azure Blob Storage
This ensures persistence of application data in Azure Container Instances
"""

import os
from datetime import datetime
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

def upload_to_azure_storage():
    """Upload logs and results to Azure Blob Storage"""
    
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    
    if not connection_string:
        print("AZURE_STORAGE_CONNECTION_STRING not set. Skipping upload.")
        return
    
    try:
        # Create the BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Container name
        container_name = os.getenv('AZURE_STORAGE_CONTAINER', 'linkedin-bot-data')
        
        # Create container if it doesn't exist
        try:
            container_client = blob_service_client.create_container(container_name)
            print(f"Created container: {container_name}")
        except Exception as e:
            container_client = blob_service_client.get_container_client(container_name)
            print(f"Using existing container: {container_name}")
        
        # Upload directories
        directories_to_upload = [
            'logs',
            'all excels',
            'recordings'
        ]
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        uploaded_files = 0
        
        for directory in directories_to_upload:
            if not os.path.exists(directory):
                continue
                
            print(f"\nUploading files from: {directory}")
            
            for root, dirs, files in os.walk(directory):
                for file in files:
                    local_path = os.path.join(root, file)
                    # Create blob path with timestamp
                    blob_path = f"runs/{timestamp}/{local_path}"
                    
                    # Upload file
                    blob_client = blob_service_client.get_blob_client(
                        container=container_name,
                        blob=blob_path
                    )
                    
                    try:
                        with open(local_path, "rb") as data:
                            blob_client.upload_blob(data, overwrite=True)
                        print(f"  Uploaded: {local_path} -> {blob_path}")
                        uploaded_files += 1
                    except Exception as e:
                        print(f"  Failed to upload {local_path}: {e}")
        
        print(f"\n✓ Successfully uploaded {uploaded_files} files to Azure Storage")
        
        # Also keep a latest copy
        for directory in directories_to_upload:
            if not os.path.exists(directory):
                continue
                
            for root, dirs, files in os.walk(directory):
                for file in files:
                    local_path = os.path.join(root, file)
                    blob_path = f"latest/{local_path}"
                    
                    blob_client = blob_service_client.get_blob_client(
                        container=container_name,
                        blob=blob_path
                    )
                    
                    try:
                        with open(local_path, "rb") as data:
                            blob_client.upload_blob(data, overwrite=True)
                    except Exception as e:
                        pass
        
        return True
        
    except Exception as e:
        print(f"Error uploading to Azure Storage: {e}")
        return False

if __name__ == "__main__":
    upload_to_azure_storage()
