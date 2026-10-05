import re
from uuid import UUID
import settings

# Custom validation error exception
class ValidationError(ValueError): pass

# =================================================================================================
# Validate a worker name
# =================================================================================================
def worker_name(name: str) -> str:

    # Raise an exception if the name is too short
    if len(name) < 1:
        raise ValidationError("Name too short")

    # Raise an exception if the name is too long
    if len(name) > 64:
        raise ValidationError("Name too long")

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

# =================================================================================================
# Validate an integer
# =================================================================================================
def integer(
    integer: int,
    minimum: int | None = None,
    maximum: int | None = None
) -> int:

    # Raise an exception if type is incorrect
    if not isinstance(integer, int):
        raise ValidationError("Invalid integer")

    # Raise an exception if the integer is too small
    if minimum:
        if integer < minimum:
            raise ValidationError("Integer too small")

    # Raise an exception if the integer is too large
    if maximum:
        if integer > maximum:
            raise ValidationError("Integer too large")

    # Return the validated integer
    return integer