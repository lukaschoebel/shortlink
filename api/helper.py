import string, random
from typing import List
from urllib.parse import urlparse


def generate_encoding(existing_encodings: List, k: int = 6) -> str:
    """Returns a randomized, short encoding which does not already exist

    Args:
        existing_encodings (List): list of all existing encodings which are currently stored
        k (int, optional): parameter which specifies the length of the generated encoding

    Returns:
        encoding (str): shortened url
    """

    if k < 1:
        raise ValueError("k has to be equal or greater than 1")

    # build alphabet of letters & digits that are used for encoding
    alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits

    # create shortened url by randomly selecting letters from alphabet
    rand_letters = random.choices(alphabet, k=k)
    encoding = "".join(rand_letters)

    # collision check
    if encoding in existing_encodings:
        # if random url already exists in memory,
        # recursively call shorten function again
        return generate_encoding()
    else:
        # ... otherwise return shortened url
        return encoding


def validate(url: str) -> bool:
    """Checks if a provided url is valid or not.

    Based on Python internal URL parsing functionality
    see: https://docs.python.org/3/library/urllib.parse.html#url-parsing

    Args:
        url (str): url that gets validated

    Returns:
        bool: url_is_valid
    """

    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
