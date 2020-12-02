
from celery.utils.log import get_task_logger
from django.contrib.sessions.backends.base import SessionBase

from pegasus.celery import app
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip

from .session import session_is_logged_in, session_get_user
from .data import download_session_clip, download_session_audio, delete_session_clip, save_video, \
    delete_session_audio, get_sql_handler, get_nosql_handler
from .models import Video

logger = get_task_logger(__name__)


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

    # Concatenate videos
    final = concatenate_videoclips(clips, method="compose")

    # Adding gamertag and logo to the video
    gamertag = ''
    gamertag_position = ''
    logo_position = ''
    text_clip = None
    logo_clip = None
    if 'gamertag' in config:
        gamertag = config['gamertag']
        gamertag_position = ['right','bottom']
    if 'logo_position' in config:
        if logo_position == ['right','bottom']:
            logo_position = ['left','bottom']
        else:
            logo_position = config['logo_position']
    else:
        logo_position = ['left','bottom']

    # if gamertag != '':
    #     text_clip = TextClip(txt='@'+gamertag, fontsize=50, font = 'Comfortaa', color='white')
    #     text_clip = text_clip.set_duration(final.duration)
    #                         .margin(right=8,top = 8, left=8, bottom=8, opacity=0)
    #                         .set_position((gamertag_position[0], gamertag_position[1]))
    logo_clip = (ImageClip('static/reels/reels-logo-white.png')
                .set_duration(final.duration)
                .resize(height=300) 
                .margin(right,=8, top = 8, left=8, bottom=8, opacity=0) 
                .set_pos((logo_position[0],logo_position[1])))

    # Combine logo, text, and videos    
    final = CompositeVideoClip([final,logo,text])

    # Add audio, only if there is audio
    audio_clip = None
    if session_audio:
        audio_clip = AudioFileClip(session_audio.local_file_path())
        # Attach audio to video, but make it only as long as the videos are
        # TODO: Manage case where videos are longer than audio clip
        final = final.set_audio(audio_clip.set_duration(final.duration))

    # === Final Saving ===

    # Write file to local storage
    video = get_sql_handler().get_video(video_id)
    final.write_videofile(filename=video.local_file_path(),
                          verbose=True,
                          codec="libx264",
                          audio_codec='aac',
                          temp_audiofile=f'temp-audio-{video.video_id}.m4a',
                          remove_temp=True,
                          preset="medium",
                          ffmpeg_params=["-profile:v", "baseline", "-level", "3.0", "-pix_fmt", "yuv420p"])
    # Save video to cold storage (and make video available in relational database)

    # close local files because we don't need them anymore and so they can be removed later
    for clip in clips:
        clip.close()

    if audio_clip:
        audio_clip.close()

    save_video(video, sync=True, clean=True)

    # Clean up remote session files
    for session_clip in session_clips:
        delete_session_clip(session_clip.clip_id)

    if session_audio:
        delete_session_audio(session_audio.audio_id)
