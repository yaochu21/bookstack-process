import re

def validate_url(url):
    """Validate URL if true return url part of the string else return False"""
    pattern = re.compile(r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)')
    if pattern.search(url):
        return pattern.search(url).group()
    return False