"""
Utils
"""
from urllib.parse import urlparse

import requests


def normalize_url(url):
    """
    URL normalize
    """
    if not url:
        return None
    res = urlparse(url)
    return f"{res.scheme}://{res.netloc}"


def get_status_code(url):
    """
    Makes a request to URL and returns status code
    Returns None when status is unseccessful
    """
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.status_code
    except requests.exceptions.RequestException:
        return None