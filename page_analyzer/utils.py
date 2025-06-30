"""
Utils
"""
from urllib.parse import urlparse


def normalize_url(url):
    """
    URL normalize
    """
    if not url:
        return None
    res = urlparse(url)
    return f"{res.scheme}://{res.netloc}"