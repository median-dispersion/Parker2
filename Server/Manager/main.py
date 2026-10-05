from wsgi import WSGI, JSONRequest, TextResponse, JSONResponse, Request
from http import HTTPStatus
import validation
from database import pool
import settings
import psycopg.errors

# Initialize the main WSGI instance
main = WSGI()

# =================================================================================================
# An endpoint for workers to connect to the server
# =================================================================================================
@main.POST("/worker/connect")
@main.requires_json({"name": validation.worker_name})
def connect_worker(request: JSONRequest) -> TextResponse | JSONResponse:

    # Get the worker name
    name = request.body_dict["name"]

    # Insert the worker into the database
    with pool.connection() as connection:
        with connection.transaction():
            worker = connection.execute(t"""
                INSERT INTO workers (name)
                VALUES({name})
                RETURNING uuid;
            """).fetchone()

    # Return the worker UUID and respond with 200 OK
    return JSONResponse(status = HTTPStatus.OK, body = worker)

# =================================================================================================
# An endpoint for workers to disconnect from the server
# =================================================================================================
@main.POST("/worker/disconnect")
@main.requires_json({"uuid": validation.uuid})
def disconnect_worker(request: JSONRequest) -> TextResponse:

    # Get the worker UUID
    uuid = request.body_dict["uuid"]

    # Disconnect the worker and terminate all jobs claimed by it
    with pool.connection() as connection:
        with connection.transaction():
            worker = connection.execute(t"""
                WITH worker AS (
                    UPDATE workers
                    SET
                        status = 'disconnected',
                        active_at = CURRENT_TIMESTAMP(6),
                        disconnected_at = CURRENT_TIMESTAMP(6)
                    WHERE uuid = {uuid}
                    AND status = 'connected'
                    RETURNING id
                ),
                terminated_jobs AS (
                    UPDATE jobs
                    SET
                        status = 'terminated',
                        terminated_at = CURRENT_TIMESTAMP(6)
                    FROM worker
                    WHERE jobs.worker_id = worker.id
                    AND jobs.status = 'claimed'
                )
                SELECT id FROM worker;
            """).fetchone()

    # If no worker is returned, i.e. no worker with the given UUID was connected
    # Respond with 400 Bad Request
    if not worker:
        return TextResponse(status = HTTPStatus.BAD_REQUEST, body = "Worker not connected")

    # Implicitly respond with 200 OK

# =================================================================================================
# An endpoint for getting the job rules
# =================================================================================================
@main.GET("/job/rules")
def job_rules(request: Request) -> JSONResponse:

    # Respond with the job rules as JSON
    return JSONResponse(
        status = HTTPStatus.OK,
        body = {
            "minimum_size": settings.job_minimum_size,
            "maximum_size": settings.job_maximum_size,
            "target_duration_seconds": settings.job_target_duration_seconds,
            "update_interval_seconds": settings.job_update_interval_seconds
        }
    )

# =================================================================================================
# An endpoint for claiming a job
# =================================================================================================
@main.POST("/job/claim")
@main.requires_json({
    "worker_uuid": validation.uuid,
    "size": {
        "function": validation.integer,
        "arguments": (
            settings.job_minimum_size,
            settings.job_maximum_size
        )
    }
})
def claim_job(request: JSONRequest) -> TextResponse | JSONResponse:

    # Get the request body
    body = request.body_dict

    # Get the worker UUID
    worker_uuid = body["worker_uuid"]

    # Get the job size
    size = body["size"]

    # Get a database connection and transaction
    with pool.connection() as connection:
        with connection.transaction():

            # Try to claim a job
            try:
                job = connection.execute(t"""
                    SELECT
                        uuid,
                        start_index,
                        end_index
                    FROM claim_job(
                        {worker_uuid},
                        {size},
                        {settings.job_update_timeout_seconds}
                    );
                """).fetchone()

            # If a database exception occurs
            except psycopg.errors.RaiseException as exception:

                # If the exception is about the worker not being connected return 400 Bad Request
                if "Worker not connected" in str(exception):
                    return TextResponse(status = HTTPStatus.BAD_REQUEST, body = "Worker not connected")

                # If the exception is about something else re-raise it
                raise

    # Return the claimed job and respond with 200 OK
    return JSONResponse(
        status = HTTPStatus.OK,
        body = {
            "uuid": str(job["uuid"]),
            "start_index": int(job["start_index"]),
            "end_index": int(job["end_index"])
        }
    )