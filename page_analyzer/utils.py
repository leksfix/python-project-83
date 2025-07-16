"""
Utils
"""
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


def normalize_url(url):
    """
    URL normalize
    """
    res = urlparse(url)
    return f"{res.scheme}://{res.netloc}"


def get_site_data(url):
    """
    Makes a request to URL and returns status code
    and other parameters of the site's page
    Returns None when status is unseccessful
    """
    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except requests.exceptions.RequestException:
        return None
    
    page_text = resp.text
    soup = BeautifulSoup(page_text, 'html.parser')
    meta_tags = soup.find_all('meta')
    
    description = None
    for tag in meta_tags:
        if tag.get("name") == "description":
            description = tag.get("content")
            break

    return {
        "status_code": resp.status_code,
        "h1": soup.h1.text if soup.h1 else None,
        "title": soup.title.string if soup.title else None,
        "description": description
    }
