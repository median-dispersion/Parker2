from wsgi import WSGI, JSONRequest, TextResponse, JSONResponse
from http import HTTPStatus
import validation
from database import pool

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
                    disconnected_at = CURRENT_TIMESTAMP(6)
                WHERE uuid = {uuid}
                AND status = 'connected';
            """)

    # If no rows where affected, i.e. the UUID did not correspond to a connected worker
    # Respond with 400 Bad Request
    if cursor.rowcount == 0:
        return TextResponse(status = HTTPStatus.BAD_REQUEST, body = "Worker not connected")

    # Implicitly respond with 200 OK