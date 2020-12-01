import os
from os import remove
from os.path import join

from celery.utils.log import get_task_logger

from pegasus.celery import app
from pegasus.settings import MEDIA_ROOT
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip

from .video import download_session_clip, download_session_audio, delete_session_clip, save_video, delete_session_audio
from .models import Video
from .sql.sql import get_sql_handler

logger = get_task_logger(__name__)


@app.task(ignore_result=True)
def make(session_key: str, user_id: str, config: dict) -> None:
    # Save video to relational database (not available yet)
    if 'file_type' not in config:
        raise KeyError('make algorithm requires file_type in configuration')
    video = Video(user_id=user_id, session_key=session_key, file_type=config['file_type'])
    get_sql_handler().insert_video(video=video)

    session_clips = get_sql_handler().get_session_clips_by_session_key(session_key)
    for session_clip in session_clips:
        download_session_clip(session_clip, sync=True)
    session_audios = get_sql_handler().get_session_audio_by_session_key(session_key)
    session_audio = None
    if session_audios:
        session_audio = session_audios[0]
        download_session_audio(session_audio, sync=True)

    # Create VideoFileClips
    clips = [VideoFileClip(session_clip.local_file_path()) for session_clip in session_clips]

    # Concatenate videos
    final = concatenate_videoclips(clips, method="compose")

    # Add audio, only if there is audio
    if session_audio:
        audio_clip = AudioFileClip(session_audio.local_file_path())
        # Attach audio to video, but make it only as long as the videos are
        # TODO: Manage case where videos are longer than audio clip
        final = final.set_audio(audio_clip.set_duration(final.duration))

    # === Final Saving ===

    # Write file to local storage
    final.write_videofile(join(MEDIA_ROOT, video.local_file_path()),
                          verbose=True,
                          codec="libx264",
                          audio_codec='aac',
                          temp_audiofile='temp-audio-{}-{}.m4a'.format(session_key, video.video_id),
                          remove_temp=True,
                          preset="medium",
                          ffmpeg_params=["-profile:v", "baseline", "-level", "3.0", "-pix_fmt", "yuv420p"])
    # Save video to cold storage (and make video available in relational database)
    save_video(video, clean=False)

    # Clean up remote session files
    for session_clip in session_clips:
        delete_session_clip(session_clip.clip_id)

    if session_audio:
        delete_session_audio(session_audio.audio_id)
