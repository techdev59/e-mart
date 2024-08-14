from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient
import os
import uuid
import hashlib
import base64

class AzureBlobStorage:
    def __init__(self):
        self.tenant_id = f"{os.environ.get('TENANT_ID')}"
        self.client_id = f"{os.environ.get('CLIENT_ID')}"
        self.client_secret = f"{os.environ.get('CLIENT_SECRET')}"
        self.container_name = f"{os.environ.get('CONTAINER_NAME')}"
        self.storage_account_name = f"{os.environ.get('STORAGE_ACCOUNT_NAME')}"
        self.blob_service_client_url = f"https://{self.storage_account_name}.blob.core.windows.net"
        self.credential = ClientSecretCredential(self.tenant_id, self.client_id, self.client_secret)
        self.blob_service_client = BlobServiceClient(account_url=self.blob_service_client_url, credential=self.credential)


    def generate_unique_id(self):
        uuid_str = str(uuid.uuid4())
        hash_object = hashlib.sha1(uuid_str.encode('utf-8'))
        uid_base64 = base64.urlsafe_b64encode(hash_object.digest())[:24].decode('utf-8')
        return f"{uid_base64}"


    def upload_file(self, image_file_path, folder_name=None):
        container_client = self.blob_service_client.get_container_client(self.container_name)
        image_name = self.generate_unique_id() + os.path.splitext(image_file_path)[1]
        # Combine folder name with the image name
        if folder_name:
            blob_name = f"{folder_name}/{image_name}"
        else:
            blob_name = image_name
        blob_client = container_client.get_blob_client(blob_name)
        with open(image_file_path, "rb") as data:
            blob_client.upload_blob(data)
        blob_url = f"https://{self.storage_account_name}.blob.core.windows.net/{self.container_name}/{blob_name}"
        return blob_url


    def list_blobs(self):
        container_client = self.blob_service_client.get_container_client(self.container_name)
        blobs = container_client.list_blobs()
        blob_list = [blob.name for blob in blobs]
        return blob_list
    
    
    def delete_blob(self, blob_name):
        container_client = self.blob_service_client.get_container_client(self.container_name)
        try:
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.delete_blob()
        except:
            print("failed to delete")