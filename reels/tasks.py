from os.path import join

from celery import shared_task
# The main algorithm file for compiling clips and audio into a montage video.
# All functions return the string location of the final compiled video
#   or empty string if no video was created
from typing import List, Union

from celery.utils.log import get_task_logger
from time import sleep

from django.core.files.storage import get_storage_class

from pegasus.celery import app
from pegasus.settings import MEDIA_URL, MEDIA_ROOT
from .migrations import *
from django.contrib.sessions.backends.base import SessionBase
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip

from .azure.blob import save_video_to_blob
from .models import SessionClip, SessionAudio, Video, User
from .session import save_session_video_name, get_session_clips, get_session_audio, session_is_logged_in, \
    session_get_user
from .azure.sql import insert_video, get_admin_user

logger = get_task_logger(__name__)


# Main function
@app.task(ignore_result=True)
def make(session_key: str, user_id: str, preset: str) -> None:
    preset = preset.lower()
    if preset == 'basic':
        make_basic(session_key, user_id)
        return None
    # if preset == 'call_of_duty_sniper':
    #     return make_call_of_duty_sniper(session, user)
    # if preset == 'rocket_league':
    #     return make_rocket_league(session, user)
    else:
        raise ValueError("This preset is not implemented")


# Simplest possible algorithm
def make_basic(session_key: str, user_id: str) -> None:
    logger.info('Starting make_basic')
    # Create VideoFileClips
    clips = [VideoFileClip(join(MEDIA_ROOT, clip.file_name)) for clip in get_session_clips(session_key)]

    logger.info('Concatenating clips')
    # Concatenate videos
    final = concatenate_videoclips(clips, method="compose")

    # Add audio, only if there is audio
    session_audio = get_session_audio(session_key)
    if session_audio:
        audio_clip = AudioFileClip(join(MEDIA_ROOT, session_audio.file_name))
        # Attach audio to video, but make it only as long as the videos are
        # TODO: Manage case where videos are longer than audio clip
        final = final.set_audio(audio_clip.set_duration(sum([clip.duration for clip in clips])))

    logger.info('Saving video')
    # === Final Saving ===
    # Create Video object for easy manipulation
    video = Video(user_id=user_id)
    # Write file to local storage
    final.write_videofile(join(MEDIA_ROOT, save_session_video_name(session_key, video.video_id)), verbose=True,
                          codec="libx264",
                          audio_codec='aac',
                          temp_audiofile='temp-audio-{}-{}.m4a'.format(session_key, video.video_id),
                          remove_temp=True,
                          preset="medium",
                          ffmpeg_params=["-profile:v", "baseline", "-level", "3.0", "-pix_fmt", "yuv420p"])
    # Save video information to relational database
    insert_video(video=video)
    # Save video to cold storage
    save_video_to_blob(video_file_location=join(MEDIA_ROOT, save_session_video_name(session_key, video.video_id)),
                       video_id=video.video_id)


# Example of complicated algorithm
def make_call_of_duty_sniper(session: SessionBase, user: User) -> Video:
    # TODO implement
    raise ValueError("This preset is not implemented")


# Rocket League Reel
def make_rocket_league(session: SessionBase, user: User) -> Video:
    # TODO implement
    raise ValueError("This preset is not implemented")

