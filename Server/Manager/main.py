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

    # Set the worker status to disconnected
    with pool.connection() as connection:
        with connection.transaction():
            cursor = connection.execute(t"""
                UPDATE workers
                SET
                    status = 'disconnected',
                    active_at = CURRENT_TIMESTAMP(6),
                    disconnected_at = CURRENT_TIMESTAMP(6)
                WHERE uuid = {uuid}
                AND status = 'connected';
            """)

    # If no rows where affected, i.e. the UUID did not correspond to a connected worker
    # Respond with 400 Bad Request
    if cursor.rowcount == 0:
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
                        {settings.job_timeout_seconds}
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