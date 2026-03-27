from pydantic import (
    BaseModel,
    constr,
    conint
)
from uuid import UUID

# =================================================================================================
# Request body for registering a client
# =================================================================================================
class ClientRegistration(BaseModel):

    client_name: constr(min_length=1, max_length=64, strip_whitespace=True)

# =================================================================================================
# Request body for claiming a job
# =================================================================================================
class JobClaim(BaseModel):

    client_uuid: UUID
    job_size: conint(gt=0)

# =================================================================================================
# Request body for updating a job
# =================================================================================================
class JobUpdate(BaseModel):

    client_uuid: UUID
    job_uuid: UUID
    current_job_index: conint(gt=0)

# =================================================================================================
# Request body for completing a job
# =================================================================================================
class JobCompletion(BaseModel):

    client_uuid: UUID
    job_uuid: UUID

# =================================================================================================
# Request body for submitting a result
# =================================================================================================
class ResultSubmission(BaseModel):

    client_uuid: UUID
    job_uuid: UUID
    a: int
    b: int
    c: int
    d: int
    e: int
    f: int
    g: int
    h: int
    i: int