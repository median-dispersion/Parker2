from fastapi import FastAPI, Depends, HTTPException
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from pydantic import constr, conint
from sqlalchemy import text
from uuid import UUID
from settings import settings

# Initialize FastAPI
api = FastAPI()

# Create the database session dependency
session_dependency = Annotated[AsyncSession, Depends(get_session)]

# =================================================================================================
# Client registration endpoint
# =================================================================================================
@api.post("/client/register")
async def register_client(
    client_name: constr(min_length=1, max_length=64, strip_whitespace=True),
    database_session: session_dependency
):

    try:

        # Insert a new client entry into the database
        client_uuid = await database_session.execute(
            text("""
                INSERT INTO clients (name)
                VALUES (:name)
                RETURNING uuid;
            """),
            {"name": client_name}
        )

        # Commit changes to database
        await database_session.commit()

        # Get the new client UUID or raise an exception if nothing was returned
        client_uuid = client_uuid.scalar_one()

    # If the client could not be inserted into the database
    except Exception:

        # Rollback database changes
        # Respond with a service temporarily unavailable
        # Force the client to retry
        await database_session.rollback()
        raise HTTPException(status_code=503)

    # Return the new client UUID
    return {"uuid": client_uuid}

# =================================================================================================
# Endpoint for claiming a new job
# =================================================================================================
@api.post("/job/claim")
async def claim_job(
    client_uuid: UUID,
    job_size: conint(gt=0),
    database_session: session_dependency
):

    try:

        # Select the client ID from the database based on the provided UUID
        client_id = await database_session.execute(
            text("""
                SELECT id
                FROM clients
                WHERE uuid = :uuid;
            """),
            {"uuid": client_uuid}
        )

        # Get the client ID or raise an exception of no ID was selected
        client_id = client_id.scalar_one()

    # If no client ID was selected
    except Exception:

        # Return with an unauthorized response
        raise HTTPException(status_code=401)

    try:

        # Update 1 'claimed' job that is associated with the current search process to 'expired' where the expiration date has been reached
        # Create a new job for this client and set its start and end index to the values of the now expired job
        # Return the UUID, start and end index of the new job
        # This ensures that every expired job is reissued as a new job and that there are no gaps in the search
        job = await database_session.execute(
            text("""
                WITH search AS (
                    SELECT id
                    FROM searches
                    WHERE end_date IS NULL
                    ORDER BY id DESC
                    LIMIT 1
                ),
                expired_job AS (
                    UPDATE jobs
                    SET state = 'expired'
                    WHERE id = (
                        SELECT jobs.id
                        FROM jobs
                        JOIN search ON search.id = jobs.search_id
                        WHERE jobs.state = 'claimed'
                        AND jobs.expiration_date <= now()
                        ORDER BY jobs.start_index ASC
                        LIMIT 1
                        FOR UPDATE SKIP LOCKED
                    )
                    RETURNING search_id, start_index, end_index
                )
                INSERT INTO jobs (
                    search_id,
                    client_id,
                    start_index,
                    current_index,
                    end_index,
                    expiration_date
                )
                SELECT
                    expired_job.search_id AS search_id,
                    :client_id AS client_id,
                    expired_job.start_index AS start_index,
                    expired_job.start_index AS current_index,
                    expired_job.end_index AS end_index,
                    now() + (:expiration_seconds * interval '1 second') AS expiration_date
                FROM expired_job
                RETURNING uuid, start_index, end_index;
            """),
            {
                "client_id": client_id,
                "expiration_seconds": settings.scheduler_job_expiration_seconds
            }
        )

        # Commit changes to the database
        await database_session.commit()

        # Get the job or None if no job was expired
        job = job.mappings().one_or_none()

    # If an exception occurs
    except Exception:

        # Rollback changes and respond with a service temporarily unavailable
        await database_session.rollback()
        raise HTTPException(status_code=503)

    # Check if no expired job was reissued
    if job is None:

        try:

            # Insert 1 new job for the current search process
            # Set the start index of the job to the next index of the current search
            # Set the end index of th job to start index + job size
            # Update the next index of the search to be the end index of the new job
            # Return the job UUID, start and end index
            job = await database_session.execute(
                text("""
                    WITH search AS (
                        SELECT id, next_index
                        FROM searches
                        WHERE end_date IS NULL
                        ORDER BY id DESC
                        LIMIT 1
                        FOR UPDATE
                    ),
                    job AS (
                        INSERT INTO jobs (
                            search_id,
                            client_id,
                            start_index,
                            current_index,
                            end_index,
                            expiration_date
                        )
                        SELECT
                            search.id AS search_id,
                            :client_id AS client_id,
                            search.next_index AS start_index,
                            search.next_index AS current_index,
                            search.next_index + :job_size AS end_index,
                            now() + (:expiration_seconds * interval '1 second') AS expiration_date
                        FROM search
                        RETURNING search_id, uuid, start_index, end_index
                    )
                    UPDATE searches
                    SET next_index = job.end_index
                    FROM job
                    WHERE id = job.search_id
                    RETURNING job.uuid, job.start_index, job.end_index;
                """),
                {
                    "client_id": client_id,
                    "job_size": job_size,
                    "expiration_seconds": settings.scheduler_job_expiration_seconds
                }
            )

            # Commit changes to the database
            await database_session.commit()

            # Get the job or raise an exception if no job was created
            job = job.mappings().one()

        # If an exception occurs
        except Exception:

            # Rollback changes and respond with a service temporarily unavailable
            await database_session.rollback()
            raise HTTPException(status_code=503)

    # Return the job
    return {
        "uuid": job["uuid"],
        "start_index": job["start_index"],
        "end_index": job["end_index"],
        "update_seconds": settings.scheduler_job_update_seconds
    }