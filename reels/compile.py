# The main algorithm file for compiling clips and audio into a montage video


# Main function
def make(session_clips, preset):
    preset = preset.lower()
    if preset == 'default':
        return make_preset(session_clips)
    if preset == 'call_of_duty_sniper':
        return make_call_of_duty_sniper()
    else:
        print("This preset is not implemented")
        return None


# Simplest possible algorithm
def make_preset(session_clips):
    # TODO implement
    pass


# Example of complicated algorithm
def make_call_of_duty_sniper(session_clips):
    pass
