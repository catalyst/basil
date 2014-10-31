import re
from validation import validator

@validator('must be a valid identifier made up of alphanumeric characters and underscores.')
def validate_identifier(value):
    """
    Returns True if value is a valid identifier made up of alphanumeric
    characters and underscores.
    """
    return bool(re.search(r'^[A-z][A-z0-9_]+$', value))
