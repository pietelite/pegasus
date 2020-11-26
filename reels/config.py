# Configuration values for application
# Keep all values alphabetized

# complete email validator
EMAIL_REGEX = r'^[^@\s]+@[^@\s\.]+\.[^@\.\s]+$'

# the maximum length for a username (inclusive)
PASSWORD_LENGTH_MAX = 20
# the minimum length for a username (inclusive)
PASSWORD_LENGTH_MIN = 6
# username validator, not including length
PASSWORD_REGEX = r'^[0-9a-zA-Z!@#\$%\^&\*\(\)\[\]\{\},\./<>\?]*$'

SUPPORTED_VIDEO_TYPES = ['mp4']
SUPPORTED_AUDIO_TYPES = ['mp3']

# the maximum length for a username (inclusive)
USERNAME_LENGTH_MAX = 20
# the minimum length for a username (inclusive)
USERNAME_LENGTH_MIN = 6
# username validator, not including length
USERNAME_REGEX = r'^[0-9a-zA-Z-_.]*$'

