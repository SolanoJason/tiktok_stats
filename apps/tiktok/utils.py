import re

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