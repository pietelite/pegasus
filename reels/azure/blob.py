import os
from azure.storage.blob import BlobServiceClient
from pegasus.celery import app
from reels.sql.sql import get_sql_handler

connection_string = os.getenv("AZURE_BLOB_CONNECTION_STRING")

VIDEO_CONTAINER_NAME = "pegasus-videos"
CLIP_CONTAINER_NAME = "pegasus-session-clips"
AUDIO_CONTAINER_NAME = "pegasus-session-audio"


# Save a local video file to azure blob storage with a given video_id
@app.task(ignore_result=True)
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
@app.task(ignore_result=True)
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
@app.task(ignore_result=True)
def _delete_in_blob(remote_name: str, container_name) -> None:
    # Instantiate a new BlobServiceClient using a connection string
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Instantiate a new ContainerClient
    container_client = blob_service_client.get_container_client(container_name)

    # Instantiate a new BlobClient
    blob_client = container_client.get_blob_client(remote_name)

    blob_client.delete_blob()


@app.task(ignore_result=True)
def save_video_to_blob(local_path: str, video_id: str):
    _save_to_blob(local_path, video_id, VIDEO_CONTAINER_NAME)

    # Make video available in database
    video = get_sql_handler().get_video(video_id)
    if not video:
        raise RuntimeError(f'Video {video_id} was saved to blob but was not found in relational database')
    video.available = True
    get_sql_handler().update_video(video)
    os.remove(local_path)


@app.task(ignore_result=True)
def download_video_from_blob(local_path: str, video_id: str):
    _download_from_blob(local_path, video_id, VIDEO_CONTAINER_NAME)


@app.task(ignore_result=True)
def delete_video_in_blob(video_id: str):
    _delete_in_blob(video_id, VIDEO_CONTAINER_NAME)

    # Make video unavailable in database
    video = get_sql_handler().get_video(video_id)
    if not video:
        return  # Ignore
    video.available = False
    get_sql_handler().update_video(video)


@app.task(ignore_result=True)
def save_clip_to_blob(local_path: str, clip_id: str):
    _save_to_blob(local_path, clip_id, CLIP_CONTAINER_NAME)

    # Make clip available in database
    clip = get_sql_handler().get_session_clip(clip_id)
    if not clip:
        raise RuntimeError(f'Clip {clip_id} was saved to blob but was not found in relational database')
    clip.available = True
    get_sql_handler().update_clip(clip)
    os.remove(local_path)


@app.task(ignore_result=True)
def download_clip_from_blob(local_path: str, clip_id: str):
    _download_from_blob(local_path, clip_id, CLIP_CONTAINER_NAME)


@app.task(ignore_result=True)
def delete_clip_in_blob(clip_id: str):
    _delete_in_blob(clip_id, CLIP_CONTAINER_NAME)

    # Make clip unavailable in database
    clip = get_sql_handler().get_session_clip(clip_id)
    if not clip:
        return  # Ignore
    clip.available = False
    get_sql_handler().update_session_clip(clip)


@app.task(ignore_result=True)
def save_audio_to_blob(local_path: str, audio_id: str):
    _save_to_blob(local_path, audio_id, AUDIO_CONTAINER_NAME)

    # Make audio available in database
    audio = get_sql_handler().get_session_audio(audio_id)
    if not audio:
        raise RuntimeError(f'Audio {audio_id} was saved to blob but was not found in relational database')
    audio.available = True
    get_sql_handler().update_session_audio(audio)
    os.remove(local_path)


@app.task(ignore_result=True)
def download_audio_from_blob(local_path: str, audio_id: str):
    _download_from_blob(local_path, audio_id, AUDIO_CONTAINER_NAME)


@app.task(ignore_result=True)
def delete_audio_in_blob(audio_id: str):
    _delete_in_blob(audio_id, AUDIO_CONTAINER_NAME)

    # Make audio unavailable in database
    audio = get_sql_handler().get_session_audio(audio_id)
    if not audio:
        return  # Ignore
    audio.available = False
    get_sql_handler().update_session_audio(audio)
