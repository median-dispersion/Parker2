from wsgi import WSGI, JSONRequest, JSONResponse, TextResponse
import validation
from database import pool
from http import HTTPStatus
import psycopg
import settings

# Initialize the main WSGI instance
main = WSGI()

# =================================================================================================
# Handle database errors and return the appropriate HTTP response
# =================================================================================================
def handle_database_errors(error: psycopg.Error) -> TextResponse:

    # If the error if of type "DatabaseError"
    if isinstance(error, psycopg.DatabaseError):

        # M0001 means there is an actual error in the program logic
        # It is not handled and instead re-raised showing up the the error log

        # If the worker is not connected respond with 400 Bad Request
        if error.sqlstate == "M0002":
            return TextResponse(status = HTTPStatus.BAD_REQUEST, body = error.diag.message_primary)

        # If no matching job was found respond with 400 Bad Request
        if error.sqlstate == "M0003":
            return TextResponse(status = HTTPStatus.BAD_REQUEST, body = error.diag.message_primary)

        # If the worker already claimed a job respond with 400 Bad Request
        if error.sqlstate == "M0004":
            return TextResponse(status = HTTPStatus.BAD_REQUEST, body = error.diag.message_primary)

    # If the error is of type "CheckViolation"
    if isinstance(error, psycopg.errors.CheckViolation):

        # If the job index is out of range respond with 400 Bad Request
        if error.diag.constraint_name == "jobs_index_check":
            return TextResponse(status = HTTPStatus.BAD_REQUEST, body = "Index out of range")

    # If the error is not handled re-raise it
    raise

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
                connection.execute(t"SELECT disconnect_worker({uuid});")

    # Handle database errors and return the appropriate HTTP response
    except psycopg.Error as error:
        return handle_database_errors(error)

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
    "size": validation.job_size
})
def claim_job(request: JSONRequest) -> TextResponse | JSONResponse:

    # Get the request body
    body = request.body_dict

    # Get the required arguments
    worker_uuid = body["worker_uuid"]
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

    # Handle database errors and return the appropriate HTTP response
    except psycopg.Error as error:
        return handle_database_errors(error)

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
    "uuid": validation.uuid,
    "attempt": validation.job_attempt,
    "worker_uuid": validation.uuid,
    "index": validation.ui64,
    "solutions": validation.ui64
})
def update_job(request: JSONRequest) -> TextResponse | None:

    # Get the request body
    body = request.body_dict

    # Get the required arguments
    uuid = body["uuid"]
    attempt = body["attempt"]
    worker_uuid = body["worker_uuid"]
    index = body["index"]
    solutions = body["solutions"]

    # Try to update the job
    try:
        with pool.connection() as connection:
            with connection.transaction():
                connection.execute(t"""
                    SELECT update_job(
                        {uuid},
                        {attempt},
                        {worker_uuid},
                        {index},
                        {solutions}
                    );
                """)

    # Handle database errors and return the appropriate HTTP response
    except psycopg.Error as error:
        return handle_database_errors(error)

# =================================================================================================
# An endpoint for canceling a job
# =================================================================================================
@main.POST("/job/cancel")
@main.requires_json({
    "uuid": validation.uuid,
    "attempt": validation.job_attempt,
    "cancellation_reason": validation.job_cancellation_reason,
    "worker_uuid": validation.uuid
})
def cancel_job(request: JSONRequest) -> TextResponse | None:

    # Get the request body
    body = request.body_dict

    # Get the required arguments
    uuid = body["uuid"]
    attempt = body["attempt"]
    cancellation_reason = body["cancellation_reason"]
    worker_uuid = body["worker_uuid"]

    # Try to cancel the job
    try:
        with pool.connection() as connection:
            with connection.transaction():
                connection.execute(t"""
                    SELECT cancel_job(
                        {uuid},
                        {attempt},
                        {cancellation_reason},
                        {worker_uuid}
                    );
                """)

    # Handle database errors and return the appropriate HTTP response
    except psycopg.Error as error:
        return handle_database_errors(error)

# =================================================================================================
# An endpoint for finishing a job
# =================================================================================================
@main.POST("/job/finish")
@main.requires_json({
    "uuid": validation.uuid,
    "attempt": validation.job_attempt,
    "worker_uuid": validation.uuid,
    "solutions": validation.ui64
})
def finish_job(request: JSONRequest) -> TextResponse | None:

    # Get the request body
    body = request.body_dict

    # Get the required arguments
    uuid = body["uuid"]
    attempt = body["attempt"]
    worker_uuid = body["worker_uuid"]
    solutions = body["solutions"]

    # Try to finish a job
    try:
        with pool.connection() as connection:
            with connection.transaction():
                connection.execute(t"""
                    SELECT finish_job(
                        {uuid},
                        {attempt},
                        {worker_uuid},
                        {solutions}
                    );
                """)

    # Handle database errors and return the appropriate HTTP response
    except psycopg.Error as error:
        return handle_database_errors(error)

# =================================================================================================
# An endpoint for submitting a solution
# =================================================================================================
@main.POST("/solution/submit")
@main.requires_json({
    "worker_uuid": validation.uuid,
    "job_uuid": validation.uuid,
    "a": validation.ui64,
    "b": validation.ui64,
    "c": validation.ui64,
    "d": validation.ui64,
    "e": validation.ui64,
    "f": validation.ui64,
    "g": validation.ui64,
    "h": validation.ui64,
    "i": validation.ui64
})
def submit_solution(request: JSONRequest):

    # Get the request body
    body = request.body_dict

    # Get the required arguments
    worker_uuid = body["worker_uuid"]
    job_uuid = body["job_uuid"]

    # Get the solution values
    a = body["a"]
    b = body["b"]
    c = body["c"]
    d = body["d"]
    e = body["e"]
    f = body["f"]
    g = body["g"]
    h = body["h"]
    i = body["i"]

    # Try to submit a solution
    try:
        with pool.connection() as connection:
            with connection.transaction():
                connection.execute(t"""
                    SELECT submit_solution(
                        {worker_uuid},
                        {job_uuid},
                        {a}, {b}, {c},
                        {d}, {e}, {f},
                        {g}, {h}, {i}
                    );
                """)

    # Handle database errors and return the appropriate HTTP response
    except psycopg.Error as error:
        return handle_database_errors(error)