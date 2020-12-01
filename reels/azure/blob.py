import os
import uuid
from datetime import datetime, timedelta

from azure.storage.blob import BlobServiceClient, BlobBlock, generate_blob_sas, generate_container_sas, \
    AccountSasPermissions, BlobSasPermissions
from pegasus.celery import app
from reels.util import uuid_to_str

connection_string = os.getenv("AZURE_BLOB_CONNECTION_STRING")

VIDEO_CONTAINER_NAME = "pegasus-videos"
CLIP_CONTAINER_NAME = "pegasus-session-clips"
AUDIO_CONTAINER_NAME = "pegasus-session-audio"


# Save a local video file to azure blob storage with a given video_id
@app.task(ignore_result=True)
def save_to_blob(local_path: str, remote_name: str, container_name) -> None:
    # Instantiate a new BlobServiceClient using a connection string
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Instantiate a new ContainerClient
    container_client = blob_service_client.get_container_client(container_name)

    # Ensure container is created
    # container_client.create_container()

    # Instantiate a new BlobClient
    blob_client = container_client.get_blob_client(remote_name)

    # Upload content to block blob
    # with open(local_path, "rb") as data:
    #     blob_client.upload_blob(data, timeout=600)

    # TODO do something like this instead
    block_list = []
    chunk_size = 4194304
    with open(local_path, "rb") as data:
        while True:
            read_data = data.read(chunk_size)
            if not read_data:
                break
            blk_id = uuid_to_str(uuid.uuid4())
            blob_client.stage_block(block_id=blk_id, data=read_data)
            block_list.append(BlobBlock(block_id=blk_id))
    blob_client.commit_block_list(block_list)


# Download a video file from azure blob storage with a given video_id
@app.task(ignore_result=True)
def download_from_blob(local_path: str, remote_name: str, container_name) -> None:
    # Instantiate a new BlobServiceClient using a connection string
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Instantiate a new ContainerClient
    container_client = blob_service_client.get_container_client(container_name)

    # Instantiate a new BlobClient
    blob_client = container_client.get_blob_client(remote_name)

    with open(local_path, "wb") as vid:
        download_stream = blob_client.download_blob(timeout=300)
        vid.write(download_stream.readall())


def get_blob_stream_url(remote_name: str, container_name: str) -> str:
    sas_token = generate_blob_sas(account_name=os.getenv('PEGASUS_BLOB_NAME'),
                                  account_key=os.getenv('PEGASUS_BLOB_KEY'),
                                  container_name=container_name,
                                  blob_name=remote_name,
                                  permission=BlobSasPermissions(read=True),
                                  expiry=datetime.utcnow() + timedelta(minutes=10))
    print(remote_name)
    return f'https://{os.getenv("PEGASUS_BLOB_NAME")}.blob.core.windows.net/{container_name}/{remote_name}?{sas_token}'


# Delete a video file in azure blob storage with a given video_id
@app.task(ignore_result=True)
def delete_in_blob(remote_name: str, container_name) -> None:
    # Instantiate a new BlobServiceClient using a connection string
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Instantiate a new ContainerClient
    container_client = blob_service_client.get_container_client(container_name)

    # Instantiate a new BlobClient
    blob_client = container_client.get_blob_client(remote_name)

    blob_client.delete_blob(timeout=30)
