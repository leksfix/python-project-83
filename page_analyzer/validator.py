"""
URL validation
"""

import validators


def validate(name):
    """
    Checks URL and returns True if OK 
    or error message if not OK
    """
    if not name:
        return "Can't be blank"
    if len(name) > 255:
        return "URL too long"
    if not validators.url(name):
        return "Incorrect URL"
    return True
