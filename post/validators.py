import re
from django.core.exceptions import ValidationError

def validate_image_size(file):
    max_size = 2
    max_size_in_bytes = max_size * 1024 * 1024

    if file.size > max_size_in_bytes:
        raise ValidationError(f"File can not be larger than {max_size}MB")
    
def validate_youtube_url(value):
    """
    Validate that the URL is a valid YouTube URL.
    Valid formats include:
    - Regular video URL: https://www.youtube.com/watch?v=VIDEO_ID
    - Shortened URL: https://youtu.be/VIDEO_ID
    - Embedded URL: https://www.youtube.com/embed/VIDEO_ID
    """
    youtube_pattern = (
        r'^(https?://)?'  # Optional http:// or https://
        r'(www\.)?'  # Optional www.
        r'(youtube\.com/watch\?.*v=[\w-]{11}'  # Standard URL with video ID
        r'|youtu\.be/[\w-]{11}'  # Shortened URL
        r'|youtube\.com/embed/[\w-]{11})'  # Embedded URL
    )
    
    if not re.match(youtube_pattern, value, re.IGNORECASE):
        raise ValidationError("Please enter a valid YouTube URL.")