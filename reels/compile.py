# The main algorithm file for compiling clips and audio into a montage video.
# All functions return the string location of the final compiled video
#   or empty string if no video was created
from .models import SessionClip, SessionAudio
from moviepy.editor import CompositeVideoClip


# Main function
def make(session_clips: list, session_audio: SessionAudio, preset: str) -> str:
    preset = preset.lower()
    if preset == 'default':
        return make_preset(session_clips, session_audio)
    if preset == 'call_of_duty_sniper':
        return make_call_of_duty_sniper(session_clips, session_audio)
    else:
        print("This preset is not implemented")
        return ''


# Simplest possible algorithm
def make_preset(session_clips: list, session_audio: SessionAudio) -> str:
    # TODO implement
    pass


# Example of complicated algorithm
def make_call_of_duty_sniper(session_clips: list, session_audio: SessionAudio) -> str:
    pass
