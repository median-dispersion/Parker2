from pydantic import BaseModel, conint
from uuid import UUID

# =================================================================================================
# Request body for updating a job
# =================================================================================================
class JobUpdate(BaseModel):

    client_uuid: UUID
    job_uuid: UUID
    current_job_index: conint(gt=0)