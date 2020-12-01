import os

from pegasus.celery import app
from reels.azure.blob import VIDEO_CONTAINER_NAME, save_to_blob, download_from_blob, delete_in_blob, \
    CLIP_CONTAINER_NAME, AUDIO_CONTAINER_NAME
from reels.models import Video, SessionClip, SessionAudio
from reels.sql.sql import get_sql_handler


# Save the video to blob storage and relational database and delete the local copy
def save_video(video: Video, sync: bool = True, clean: bool = True) -> None:
    if not get_sql_handler().get_video(video.video_id):
        get_sql_handler().insert_video(video)

    if sync:
        _save_video_worker(video.local_file_path(), video.video_id, clean)
    else:
        _save_video_worker.delay(video.local_file_path(), video.video_id, clean)


@app.task(ignore_result=True)
def _save_video_worker(local_path, video_id, clean):
    save_to_blob(local_path, video_id, VIDEO_CONTAINER_NAME)

    # Make video available in database
    video = get_sql_handler().get_video(video_id)
    if not video:
        raise RuntimeError(f'Video {video_id} was saved to blob but was not found in relational database')
    video.available = True
    get_sql_handler().update_video(video)
    if clean and os.path.exists(video.local_file_path()):
        os.remove(video.local_file_path())


# Downloads a video to its local file location
def download_video(video: Video, sync: bool = True) -> None:
    if os.path.exists(video.local_file_path()):
        return  # Already have this file in store

    if sync:
        download_from_blob(video.local_file_path(), video.video_id, VIDEO_CONTAINER_NAME)
    else:
        download_from_blob.delay(video.local_file_path(), video.video_id, VIDEO_CONTAINER_NAME)


# Deletes a video from blob storage and relational database
def delete_video(video_id: str, sync: bool = True) -> None:
    video = get_sql_handler().get_video(video_id)
    if video:
        get_sql_handler().delete_video(video_id)
        if os.path.exists(video.local_file_path()):
            os.remove(video.local_file_path())

    if sync:
        delete_in_blob(video_id, VIDEO_CONTAINER_NAME)
    else:
        delete_in_blob.delay(video_id, VIDEO_CONTAINER_NAME)


# Save the clip to blob storage and relational database and delete the local copy
def save_session_clip(clip: SessionClip, sync: bool = True, clean: bool = True) -> None:
    if not get_sql_handler().get_session_clip(clip.clip_id):
        get_sql_handler().insert_session_clip(clip)

    if sync:
        _save_session_clip_worker(clip.local_file_path(), clip.clip_id, clean)
    else:
        _save_session_clip_worker.delay(clip.local_file_path(), clip.clip_id, clean)


@app.task(ignore_result=True)
def _save_session_clip_worker(local_path, clip_id, clean):
    save_to_blob(local_path, clip_id, CLIP_CONTAINER_NAME)

    # Make clip available in database
    clip = get_sql_handler().get_session_clip(clip_id)
    if not clip:
        raise RuntimeError(f'Clip {clip_id} was saved to blob but was not found in relational database')
    clip.available = True
    get_sql_handler().update_session_clip(clip)
    if clean and os.path.exists(clip.local_file_path()):
        os.remove(clip.local_file_path())


# Downloads a clip to its local file location
def download_session_clip(clip: SessionClip, sync: bool = True) -> None:
    if os.path.exists(clip.local_file_path()):
        return  # Already have this file in store

    if sync:
        download_from_blob(clip.local_file_path(), clip.clip_id, CLIP_CONTAINER_NAME)
    else:
        download_from_blob.delay(clip.local_file_path(), clip.clip_id, CLIP_CONTAINER_NAME)


# Deletes a clip from blob storage and relational database
def delete_session_clip(clip_id: str, sync: bool = True) -> None:
    session_clip = get_sql_handler().get_session_clip(clip_id)
    if session_clip:
        get_sql_handler().delete_session_clip(clip_id)
        if os.path.exists(session_clip.local_file_path()):
            os.remove(session_clip.local_file_path())

    if sync:
        delete_in_blob(clip_id, CLIP_CONTAINER_NAME)
    else:
        delete_in_blob.delay(clip_id, CLIP_CONTAINER_NAME)


# Save the audio to blob storage and relational database and delete the local copy
def save_session_audio(audio: SessionAudio, sync: bool = True, clean: bool = True) -> None:
    if not get_sql_handler().get_session_audio(audio.audio_id):
        get_sql_handler().insert_session_audio(audio)

    if sync:
        _save_session_audio_worker(audio.local_file_path(), audio.audio_id, clean)
    else:
        _save_session_audio_worker.delay(audio.local_file_path(), audio.audio_id, clean)


@app.task(ignore_result=True)
def _save_session_audio_worker(local_path, audio_id, clean):
    save_to_blob(local_path, audio_id, AUDIO_CONTAINER_NAME)

    # Make audio available in database
    audio = get_sql_handler().get_session_audio(audio_id)
    if not audio:
        raise RuntimeError(f'Audio {audio_id} was saved to blob but was not found in relational database')
    audio.available = True
    get_sql_handler().update_session_audio(audio)
    if clean and os.path.exists(audio.local_file_path()):
        os.remove(audio.local_file_path())


# Downloads audio to its local file location
def download_session_audio(audio: SessionAudio, sync: bool = True) -> None:
    if os.path.exists(audio.local_file_path()):
        return  # Already have this file in store

    if sync:
        download_from_blob(audio.local_file_path(), audio.audio_id, AUDIO_CONTAINER_NAME)
    else:
        download_from_blob.delay(audio.local_file_path(), audio.audio_id, AUDIO_CONTAINER_NAME)


# Deletes audio from blob storage and relational database
def delete_session_audio(audio_id: str, sync: bool = True) -> None:
    session_audio = get_sql_handler().get_session_audio(audio_id)
    if session_audio:
        get_sql_handler().delete_session_audio(audio_id)
        if os.path.exists(session_audio):
            os.remove(session_audio.local_file_path())

    if sync:
        delete_in_blob(audio_id, AUDIO_CONTAINER_NAME)
    else:
        delete_in_blob.delay(audio_id, AUDIO_CONTAINER_NAME)
