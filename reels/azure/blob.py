import os
from azure.storage.blob import BlobServiceClient

connection_string = os.getenv("AZURE_BLOB_CONNECTION_STRING")

VIDEO_CONTAINER_NAME = "pegasus-videos"
CLIP_CONTAINER_NAME = "pegasus-session-clips"
AUDIO_CONTAINER_NAME = "pegasus-session-audio"


# Save a local video file to azure blob storage with a given video_id
def _save_to_blob(local_path: str, remote_name: str, container_name) -> None:
    # Instantiate a new BlobServiceClient using a connection string
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Instantiate a new ContainerClient
    container_client = blob_service_client.get_container_client(container_name)

    # Ensure container is created
    # container_client.create_container()

    # Instantiate a new BlobClient
    blob_client = container_client.get_blob_client(remote_name)

    # Upload content to block blob
    with open(local_path, "rb") as data:
        blob_client.upload_blob(data)


# Download a video file from azure blob storage with a given video_id
def _download_from_blob(local_path: str, remote_name: str, container_name) -> None:
    # Instantiate a new BlobServiceClient using a connection string
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Instantiate a new ContainerClient
    container_client = blob_service_client.get_container_client(container_name)

    # Instantiate a new BlobClient
    blob_client = container_client.get_blob_client(remote_name)

    with open(local_path, "wb") as vid:
        download_stream = blob_client.download_blob()
        vid.write(download_stream.readall())


# Delete a video file in azure blob storage with a given video_id
def _delete_in_blob(remote_name: str, container_name) -> None:
    # Instantiate a new BlobServiceClient using a connection string
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Instantiate a new ContainerClient
    container_client = blob_service_client.get_container_client(container_name)

    # Instantiate a new BlobClient
    blob_client = container_client.get_blob_client(remote_name)

    blob_client.delete_blob()


def save_video_to_blob(local_path: str, video_id: str):
    _save_to_blob(local_path, video_id, VIDEO_CONTAINER_NAME)


def download_video_from_blob(local_path: str, video_id: str):
    _download_from_blob(local_path, video_id, VIDEO_CONTAINER_NAME)


def delete_video_in_blob(video_id: str):
    _delete_in_blob(video_id, VIDEO_CONTAINER_NAME)


def save_clip_to_blob(local_path: str, clip_id: str):
    _save_to_blob(local_path, clip_id, CLIP_CONTAINER_NAME)


def download_clip_from_blob(local_path: str, clip_id: str):
    _download_from_blob(local_path, clip_id, CLIP_CONTAINER_NAME)


def delete_clip_in_blob(clip_id: str):
    _delete_in_blob(clip_id, CLIP_CONTAINER_NAME)


def save_audio_to_blob(local_path: str, audio_id: str):
    _save_to_blob(local_path, audio_id, AUDIO_CONTAINER_NAME)


def download_audio_from_blob(local_path: str, audio_id: str):
    _download_from_blob(local_path, audio_id, AUDIO_CONTAINER_NAME)


def delete_audio_in_blob(audio_id: str):
    _delete_in_blob(audio_id, AUDIO_CONTAINER_NAME)
