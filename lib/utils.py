import re

def validate_url(url):
    """Validate URL if true return url part of the string else return False"""
    pattern = re.compile(r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)')
    if pattern.search(url):
        return pattern.search(url).group()
    return False

def validate_length(string, length):
    """Validate length of the string"""
    return True if len(string) <= length else False

def validate(input):
    """
    Validate the input string is a url
    """
    if not validate_url(input):
        raise ValueError("Input is not a valid url")
    if not validate_length(input, 300):
        raise ValueError("Input is too long")
    return input