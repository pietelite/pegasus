# The main algorithm file for compiling clips and audio into a montage video.
# All functions return the string location of the final compiled video
#   or empty string if no video was created
from django.contrib.sessions.backends.base import SessionBase
from .models import SessionClip, SessionAudio, Video
from moviepy.editor import CompositeVideoClip
from .session import session_is_logged_in, session_get_user


# Main function
def make(session: SessionBase, session_clips: list, session_audio: SessionAudio, preset: str) -> Video:
    preset = preset.lower()

    #Getting the user_id: If logged in, then use that, otherwise use the PEGASUS user which is 32 zeroes.
    user_id = ''
    if session_is_logged_in(session):
        user_id = session_get_user(session).user_id 
    else:
        user_id = '0'*32

    
    if preset == 'default':
        return make_preset(session_clips, session_audio,user_id)
    if preset == 'call_of_duty_sniper':
        return make_call_of_duty_sniper(session_clips, session_audio, user_id)
    else:
        print("This preset is not implemented")
        return ''


# Simplest possible algorithm
def make_default(session_clips: list, session_audio: SessionAudio, user_id: str) -> Video:
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
    
    final.write_videofile('compiled.mp4',verbose=True,
                            codec="libx264",
                            audio_codec='aac',
                            temp_audiofile='temp-audio.m4a',
                            remove_temp=True, 
                            preset="medium",
                            ffmpeg_params=["-profile:v","baseline", "-level","3.0","-pix_fmt", "yuv420p"])
    
    video = Video(user_id = user_id)
    save_video_to_blob(video_file_location= 'compiled.mp4', video_id = video.video_id)

    return video


# Example of complicated algorithm
def make_call_of_duty_sniper(session_clips: list, session_audio: SessionAudio, user_id: str) -> Video:
    pass
