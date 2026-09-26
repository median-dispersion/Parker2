import re
from uuid import UUID

# Custom validation error exception
class ValidationError(ValueError): pass

# =================================================================================================
# Validate a worker name
# =================================================================================================
def worker_name(name: str) -> str:

    # Raise an exception if the name is to short
    if len(name) < 1:
        raise ValidationError("Name to short")

    # Raise an exception if the name is to long
    if len(name) > 64:
        raise ValidationError("Name to long")

    # Raise an exception if the name contains illegal characters
    if not re.fullmatch("[a-zA-Z0-9-]+", name):
        raise ValidationError("Invalid name")

    # Return the worker name
    return name

# =================================================================================================
# Validate a UUID
# =================================================================================================
def uuid(uuid: str) -> UUID:

    # Try to parse the UUID
    try:
        uuid = UUID(uuid)

    # Raise an exception if the UUID is not parsable
    except ValueError:
        raise ValidationError("Invalid UUID")

    # Return the parsed UUID
    return uuid