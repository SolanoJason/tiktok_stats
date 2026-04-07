import re
from urllib.parse import urlparse, parse_qs

def extract_tiktok_username(url: str) -> str | None:
    """
    Extracts the username from a TikTok video URL.
    Example: https://www.tiktok.com/@mamiofertass/video/123 -> mamiofertass
    """
    # Pattern looks for '@' followed by alphanumeric characters, underscores, or dots
    pattern = r"@([a-zA-Z0-9._]+)"
    
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


def extract_video_id(url: str) -> str | None:
    """
    Extracts the video ID from a TikTok video URL.
    Example: https://www.tiktok.com/@user/video/7123456789 -> 7123456789
    """
    # Pattern looks for /video/ followed by digits
    pattern = r"/video/(\d+)"
    
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


def validate_tiktok_url(url: str) -> bool:
    """
    Validates if the URL is a valid TikTok video URL.
    """
    if not url:
        return False
    
    # Check if it's a valid URL
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
    except Exception:
        return False
    
    # Check if domain is tiktok.com or vt.tiktok.com
    is_tiktok_domain = parsed.netloc in ['www.tiktok.com', 'tiktok.com', 'vt.tiktok.com', 'm.tiktok.com']
    if not is_tiktok_domain:
        return False
    
    # Extract username and video ID to ensure it's a valid video URL
    username = extract_tiktok_username(url)
    video_id = extract_video_id(url)
    
    return username is not None and video_id is not None


def normalize_tiktok_url(url: str) -> str:
    """
    Normalizes a TikTok video URL to a standard format.
    Returns the URL with consistent format.
    """
    # Extract username and video ID
    username = extract_tiktok_username(url)
    video_id = extract_video_id(url)
    
    if not username or not video_id:
        return url
    
    # Return normalized URL format
    return f"https://www.tiktok.com/@{username}/video/{video_id}"