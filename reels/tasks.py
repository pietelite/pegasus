from celery.utils.log import get_task_logger
from django.contrib.sessions.backends.base import SessionBase
from moviepy.video.VideoClip import ImageClip, TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx.resize import resize

from pegasus.celery import app
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.editor import vfx
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
import numpy as np
from scipy.io.wavfile import read, write
import random

from .session import session_is_logged_in, session_get_user
from .data import download_session_clip, download_session_audio, delete_session_clip, save_video, \
    delete_session_audio, get_sql_handler, get_nosql_handler
from .models import Video
from .util import get_file_type

logger = get_task_logger(__name__)


def invert_colors(image):
    presets = [[0, 0, 0], [0, 2, 1]]
    usethis = random.randrange(0, len(presets), 1)
    return image[:, :, presets[usethis]]


def compile_video(session: SessionBase, config: dict) -> None:
    # Get user info
    if session_is_logged_in(session):
        user = session_get_user(session)
    else:
        user = get_sql_handler().get_admin_user()

    # Save video to relational database (not available yet)
    video = Video(user_id=user.user_id, session_key=session.session_key, file_type=config.get('file_type', 'mp4'))
    get_sql_handler().insert_video(video=video)
    get_nosql_handler().insert_video_config(video.video_id, config)

    _compile_worker.delay(session.session_key, video.video_id)


@app.task(ignore_result=True)
def _compile_worker(session_key: str, video_id: str) -> None:
    # Use this for conditional creation
    config = get_nosql_handler().get_video_config(video_id)

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
    total_duration = sum([clip.duration for clip in clips])

    # Make all clips the same size
    final_w = min([clip.w for clip in clips])
    final_h = min([clip.h for clip in clips])
    clips = [resize(clip, newsize=(final_w, final_h)) for clip in clips]

    # Adding gamertag and logo to the video
    # gamertag = config.get('gamertag', '')
    # gamertag_position = config.get('gamertag_position', ['right', 'bottom'])
    #
    # if gamertag != '':
    #     gamertag_clip = TextClip(txt='@'+gamertag, fontsize=50, font = 'Comfortaa', color='white')
    #     gamertag_clip = gamertag_clip.set_duration(final.duration)\
    #                         .margin(right=8,top = 8, left=8, bottom=8, opacity=0)\
    #                         .set_position((gamertag_position[0], gamertag_position[1])

    # === WATERMARK ===
    logo_position = config.get('logo_position', ['left', 'top'])
    logo_clip = ImageClip('./reels/static/reels/reels-logo-white.png')
    logo_clip = resize(logo_clip, height=final_h / 5)
    try:
        logo_x = (0 if logo_position[0] == 'left' else final_w - logo_clip.w)
        logo_y = (0 if logo_position[1] == 'top' else final_h - logo_clip.h)
    except (KeyError, TypeError):
        logo_x, logo_y = 0, final_h - logo_clip.h
    logo_clip = logo_clip.set_pos((logo_x, logo_y))
    clips = [CompositeVideoClip([clip, logo_clip.set_duration(clip.duration)]) for clip in clips]

    # Concatenate clips
    final = concatenate_videoclips(clips, method="compose")

    # Add audio, only if there is audio
    audio_clip = None
    if session_audio:
        audio_clip = AudioFileClip(session_audio.local_file_path())
        audio_clip = audio_clip \
            .set_start(config.get('audio_start', 0)) \
            .set_end(config.get('audio_end', audio_clip.duration))
        # Attach audio to video, but make it only as long as the videos are
        # TODO: Manage case where videos are longer than audio clip
        final = final.set_audio(audio_clip.set_duration(final.duration))

    # If extra editing is enabled, do so
    if config.get('extras', False) and session_audio and get_file_type(session_audio.local_file_path()) == 'wav':
        fs, data = read(session_audio.local_file_path())
        data = data[:, 0]
        data = data[:len(data) - len(data) % 48000]
        data2 = np.mean(data.reshape(-1, int(48000 / 4)), axis=1)
        x = np.diff(data2, n=1)
        secs = np.where(x > 200)[0]
        t = list(secs[np.where(np.diff(secs) > 12)[0] + 1])
        if np.diff(secs)[0] > 12:
            t.insert(0, secs[0])
        for i in range(0, len(t)):
            t[i] /= 4
        for i in t:
            tfreeze = i
            if tfreeze + 1.75 >= final.duration:
                break
            clip_before = final.subclip(t_end=tfreeze)
            clip_after = final.subclip(t_start=tfreeze + 1)
            clip = final.subclip(t_start=tfreeze, t_end=tfreeze + 1)
            if int(i) % 2 == 0:
                clip = clip.fl_image(invert_colors).crossfadein(0.5).crossfadeout(0.5)
            else:
                clip = clip.fx(vfx.painting, saturation=1.6, black=0.006).crossfadein(0.5).crossfadeout(0.5)
            final = concatenate_videoclips([clip_before,
                                            clip,
                                            clip_after])
    else:
        pass

    # === Final Saving ===
    video = get_sql_handler().get_video(video_id)
    final.write_videofile(filename=video.local_file_path(),
                          verbose=True,
                          codec="libx264",
                          audio_codec='aac',
                          temp_audiofile=f'temp-audio-{video.video_id}.m4a',
                          remove_temp=True,
                          preset="medium",
                          ffmpeg_params=["-profile:v", "baseline", "-level", "3.0", "-pix_fmt", "yuv420p"])
    # close local files because we don't need them anymore and so they can be removed later
    for clip in clips:
        clip.close()

    if audio_clip:
        audio_clip.close()
    # upload to cold storage
    save_video(video, sync=True, clean=False)

    # Skip for now so we can see the entries
    # # Clean up remote session files
    # for session_clip in session_clips:
    #     delete_session_clip(session_clip.clip_id)
    #
    # if session_audio:
    #     delete_session_audio(session_audio.audio_id)
