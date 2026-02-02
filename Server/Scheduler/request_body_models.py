from pydantic import BaseModel, constr, conint
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