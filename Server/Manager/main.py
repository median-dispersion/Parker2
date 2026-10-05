from wsgi import WSGI, JSONRequest, JSONResponse, TextResponse
import validation
from database import pool
from http import HTTPStatus
import psycopg
import settings

# Initialize the main WSGI instance
main = WSGI()

# =================================================================================================
# An endpoint for workers to connect to the manager
# =================================================================================================
@main.POST("/worker/connect")
@main.requires_json({"name": validation.worker_name})
def connect_worker(request: JSONRequest) -> JSONResponse:

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
# An endpoint for workers to disconnect from the manager
# =================================================================================================
@main.POST("/worker/disconnect")
@main.requires_json({"uuid": validation.uuid})
def disconnect_worker(request: JSONRequest) -> TextResponse | None:

    # Get the worker UUID
    uuid = request.body_dict["uuid"]

    # Try to disconnect the worker
    try:
        with pool.connection() as connection:
            with connection.transaction():
                connection.execute(t"""
                    SELECT disconnect_worker({uuid});
                """)

    # Catch database exceptions
    except psycopg.errors.RaiseException as exception:

        # If the worker is not connected respond with 400 Bad Request
        if exception.diag.message_primary == "Worker not connected":
            return TextResponse(status = HTTPStatus.BAD_REQUEST, body = "Worker not connected")

        # If the exception is about something else respond re-raise it
        raise

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

    # Try to claim a job
    try:
        with pool.connection() as connection:
            with connection.transaction():
                job = connection.execute(t"""
                    SELECT
                        uuid,
                        attempt,
                        start_index,
                        end_index
                    FROM claim_job(
                        {worker_uuid},
                        {size},
                        {settings.job_update_timeout_seconds}
                    );
                """).fetchone()

    # Catch database exceptions
    except psycopg.errors.RaiseException as exception:

        # If the worker is not connected respond with 400 Bad Request
        if exception.diag.message_primary == "Worker not connected":
            return TextResponse(status = HTTPStatus.BAD_REQUEST, body = "Worker not connected")

        # If the worker already claimed a job respond with 400 Bad Request
        if exception.diag.message_primary == "Worker already claimed a job":
            return TextResponse(status = HTTPStatus.BAD_REQUEST, body = "Worker already claimed a job")

        # If the exception is about something else respond re-raise it
        raise

    # Return the claimed job and respond with 200 OK
    return JSONResponse(
        status = HTTPStatus.OK,
        body = {
            "uuid": str(job["uuid"]),
            "attempt": int(job["attempt"]),
            "start_index": int(job["start_index"]),
            "end_index": int(job["end_index"])
        }
    )

# =================================================================================================
# An endpoint for updating a job
# =================================================================================================
@main.POST("/job/update")
@main.requires_json({
    "job_uuid": validation.uuid,
    "attempt": {
        "function": validation.integer,
        "arguments": (1, 9223372036854775807)
    },
    "worker_uuid": validation.uuid,
    "index": {
        "function": validation.integer,
        "arguments": (0, 18446744073709551615)
    },
    "solutions": {
        "function": validation.integer,
        "arguments": (0, 18446744073709551615)
    }
})
def update_job(request: JSONRequest) -> TextResponse | None:

    # Get the request body
    body = request.body_dict

    # Get the job UUID
    job_uuid = body["job_uuid"]

    # Get the job attempt count
    attempt = body["attempt"]

    # Get the worker UUID
    worker_uuid = body["worker_uuid"]

    # Get the current search index
    index = body["index"]

    # Get the number of found solutions
    solutions = body["solutions"]

    # Try to update the job
    try:
        with pool.connection() as connection:
            with connection.transaction():
                connection.execute(t"""
                    SELECT update_job(
                        {job_uuid},
                        {attempt},
                        {worker_uuid},
                        {index},
                        {solutions}
                    );
                """)

    # Catch database errors
    except psycopg.Error as exception:

        # The exception if of type RaiseException
        if isinstance(exception, psycopg.errors.RaiseException):

            # If the worker is not connected respond with 400 Bad Request
            if exception.diag.message_primary == "Worker not connected":
                return TextResponse(status = HTTPStatus.BAD_REQUEST, body = "Worker not connected")

            # If the job is not claimed by the worker respond with 400 Bad Request
            if exception.diag.message_primary == "No matching job":
                return TextResponse(status = HTTPStatus.BAD_REQUEST, body = "No matching job")

        # If the current search index is out of range respond with 400 Bad Request
        if isinstance(exception, psycopg.errors.CheckViolation):
            if exception.diag.constraint_name == "jobs_index_check":
                return TextResponse(status = HTTPStatus.BAD_REQUEST, body = "Index out of range")

        # If the exception is about something else respond re-raise it
        raise