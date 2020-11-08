import os
from azure.storage.blob import BlobServiceClient

connection_string = os.getenv("AZURE_BLOB_CONNECTION_STRING")

container_name = "videos"


# Save a local video file to azure blob storage with a given video_id
def save_video_to_blob(video_file_location: str, video_id: str) -> None:
    # Instantiate a new BlobServiceClient using a connection string
    blob_service_client = BlobServiceClient.from_connection_string(connection_string);

    # Instantiate a new ContainerClient
    container_client = blob_service_client.get_container_client(container_name)

    # Ensure container is created
    container_client.create_container()

    # Instantiate a new BlobClient
    blob_client = container_client.get_blob_client(video_id)

    # Upload content to block blob
    with open(video_file_location, "rb") as data:
        blob_client.upload_blob(data, blob_type="BlockBlob")


# Download a video file from azure blob storage with a given video_id
def download_video_from_blob(video_file_location: str, video_id: str) -> None:
    # Instantiate a new BlobServiceClient using a connection string
    blob_service_client = BlobServiceClient.from_connection_string(connection_string);

    # Instantiate a new ContainerClient
    container_client = blob_service_client.get_container_client(container_name)

    # Instantiate a new BlobClient
    blob_client = container_client.get_blob_client(video_id)

    with open(video_file_location, "wb") as vid:
        download_stream = blob_client.download_blob()
        vid.write(download_stream.readall())


# Delete a video file in azure blob storage with a given video_id
def delete_video_in_blob(video_id: str) -> None:
    # Instantiate a new BlobServiceClient using a connection string
    blob_service_client = BlobServiceClient.from_connection_string(connection_string);

    # Instantiate a new ContainerClient
    container_client = blob_service_client.get_container_client(container_name)

    # Instantiate a new BlobClient
    blob_client = container_client.get_blob_client(video_id)

    blob_client.delete_blob()

