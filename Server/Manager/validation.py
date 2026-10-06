import re
from uuid import UUID
import settings

# Custom validation error exception
class ValidationError(ValueError): pass

# =================================================================================================
# Validate a worker name
# =================================================================================================
def worker_name(name: str) -> str:

    # Raise an exception if the name is not a string
    if not isinstance(name, str):
        raise ValidationError("Name is not a string")

    # Raise an exception if the name is too short
    if len(name) < 1:
        raise ValidationError("Name too short")

    # Raise an exception if the name is too long
    if len(name) > 64:
        raise ValidationError("Name too long")

    # Raise an exception if the name contains illegal characters
    if not re.fullmatch("[a-zA-Z0-9-]+", name):
        raise ValidationError("Illegal characters in name")

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
        raise ValidationError("Value is not an integer")

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

# =================================================================================================
# Cancellation reason
# =================================================================================================
def cancellation_reason(reason: str) -> str:

    # Raise an exception if the reason is not a string
    if not isinstance(reason, str):
        raise ValidationError("Reason is not a string")

    # Raise an exception if the reason is missing / too short
    if len(reason) < 1:
        raise ValidationError("Missing reason")

    # If the reason is too long clip it to a maximum of 1 million characters (roughly 1 MB of text)
    if len(reason) > 1_000_000:
        reason = reason[:1_000_000]

    # Return the validated reason
    return reason