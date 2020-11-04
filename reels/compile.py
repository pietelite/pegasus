# The main algorithm file for compiling clips and audio into a montage video.
# All functions return the string location of the final compiled video
#   or empty string if no video was created
from typing import List, Union

from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip

from .azure import save_video_to_blob
from .models import SessionClip, SessionAudio, Video
from moviepy.editor import CompositeVideoClip
from .session import session_is_logged_in, session_get_user, save_session_video_location
from .sql import get_admin_user, insert_video


# Main function
def make(session_key: str, user_id: str, session_clips: List[SessionClip], session_audio: SessionAudio, preset: str) -> \
Union[Video, None]:
    preset = preset.lower()

    if preset == 'default':
        return make_default(session_key, user_id, session_clips, session_audio)
    if preset == 'call_of_duty_sniper':
        return make_call_of_duty_sniper(session_key, user_id, session_clips, session_audio)
    if preset == 'rocket_league':
        return make_rocket_league(session_key, user_id, session_clips, session_audio)
    else:
        print("This preset is not implemented")
        return None


# Simplest possible algorithm
def make_default(session_key: str, user_id: str, session_clips: List[SessionClip],
                 session_audio: SessionAudio, audio_clip=None) -> Video:
    # TODO implement

    paths = [clip.location for clip in session_clips]
    clips = []
    total_length = 0
    for element in paths:
        clip = VideoFileClip(element)
        total_length += clip.duration
        clips.append(clip)

    final = concatenate_videoclips(clips, method="compose")

    if audio_clip is None:
        audio_clip = AudioFileClip(session_audio.location)
        final = final.set_audio(audio_clip.set_duration(total_length))

    # === Final Saving ===
    # Create Video object for easy manipulation
    video = Video(user_id=user_id)
    # Write file to local storage
    final.write_videofile(save_session_video_location(session_key, video.video_id), verbose=True,
                          codec="libx264",
                          audio_codec='aac',
                          temp_audiofile='temp-audio.m4a',
                          remove_temp=True,
                          preset="medium",
                          ffmpeg_params=["-profile:v", "baseline", "-level", "3.0", "-pix_fmt", "yuv420p"])
    # Save video information to relational database
    insert_video(video=video)
    # Save video to cold storage
    save_video_to_blob(video_file_location=save_session_video_location(session_key, video.video_id),
                       video_id=video.video_id)

    return video


# Example of complicated algorithm
def make_call_of_duty_sniper(session_key: str, user_id: str, session_clips: list, session_audio: SessionAudio) -> Video:
    # TODO implement
    pass


# Rocket League Reel
def make_rocket_league(session_key: str, user_id: str, session_clips: list, session_audio: SessionAudio) -> Video:
    # TODO implement
    pass
