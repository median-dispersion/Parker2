from wsgi import JSONArgumentValidator
import re
from uuid import UUID
import settings

# =================================================================================================
# Validate a worker name
# =================================================================================================
def validate_worker_name(name: str) -> str:

    # Raise an exception if the name is not a string
    if not isinstance(name, str):
        raise JSONArgumentValidator.ValidationError("Name is not a string")

    # Raise an exception if the name is too short
    if len(name) < 1:
        raise JSONArgumentValidator.ValidationError("Name too short")

    # Raise an exception if the name is too long
    if len(name) > 64:
        raise JSONArgumentValidator.ValidationError("Name too long")

    # Raise an exception if the name contains illegal characters
    if not re.fullmatch("[a-zA-Z0-9-]+", name):
        raise JSONArgumentValidator.ValidationError("Illegal characters in name")

    # Return the worker name
    return name

# =================================================================================================
# Validate a UUID
# =================================================================================================
def validate_uuid(uuid: str) -> UUID:

    # Raise an exception if the UUID is not a string
    if not isinstance(uuid, str):
        raise JSONArgumentValidator.ValidationError("UUID is not a string")

    # Try to parse the UUID
    try:
        uuid = UUID(uuid)

    # Raise an exception if the UUID is not parsable
    except ValueError:
        raise JSONArgumentValidator.ValidationError("Invalid UUID")

    # Return the parsed UUID
    return uuid

# =================================================================================================
# Validate an integer
# =================================================================================================
def validate_integer(
    integer: int,
    minimum: int | None = None,
    maximum: int | None = None
) -> int:

    # Raise an exception if type is incorrect
    if not isinstance(integer, int):
        raise JSONArgumentValidator.ValidationError("Value is not an integer")

    # Raise an exception if the integer is too small
    if minimum != None:
        if integer < minimum:
            raise JSONArgumentValidator.ValidationError("Integer too small")

    # Raise an exception if the integer is too large
    if maximum != None:
        if integer > maximum:
            raise JSONArgumentValidator.ValidationError("Integer too large")

    # Return the validated integer
    return integer

# =================================================================================================
# Validate a cancellation reason
# =================================================================================================
def validate_cancellation_reason(reason: str) -> str:

    # Raise an exception if the reason is not a string
    if not isinstance(reason, str):
        raise JSONArgumentValidator.ValidationError("Cancellation reason is not a string")

    # Raise an exception if the reason is missing / too short
    if len(reason) < 1:
        raise JSONArgumentValidator.ValidationError("Cancellation reason is empty")

    # If the reason is too long clip it to a maximum of 1 million characters (roughly 1 MB of text)
    if len(reason) > 1_000_000:
        reason = reason[:1_000_000]

    # Return the validated reason
    return reason

# JSON argument validators
worker_name = JSONArgumentValidator(validate_worker_name)
uuid = JSONArgumentValidator(validate_uuid)
job_size = JSONArgumentValidator(validate_integer, (settings.job_minimum_size, settings.job_maximum_size))
job_attempt = JSONArgumentValidator(validate_integer, (1, 9223372036854775807))
ui64 = JSONArgumentValidator(validate_integer, (0, 18446744073709551615))
job_cancellation_reason = JSONArgumentValidator(validate_cancellation_reason)