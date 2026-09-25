from wsgi import WSGI, JSONRequest, TextResponse, JSONResponse
from http import HTTPStatus
import re
from database import pool
from uuid import UUID

# Initialize the main WSGI instance
main = WSGI()

# =================================================================================================
# An endpoint for workers to connect to the server
# =================================================================================================
@main.POST("/worker/connect")
@main.requires_json
def connect_worker(request: JSONRequest) -> TextResponse | JSONResponse:

    # Get the JSON body
    body = request.body_dict

    # Get the worker name
    name = body.get("name")

    # If no name was provided respond with 400 Bad Request
    if not name:
        return TextResponse(status = HTTPStatus.BAD_REQUEST, body = "Missing name")

    # If the name is to short respond with 400 Bad Request
    if len(name) < 1:
        return TextResponse(status = HTTPStatus.BAD_REQUEST, body = "Name to short")

    # If the name is to long respond with 400 Bad Request
    if len(name) > 64:
        return TextResponse(status = HTTPStatus.BAD_REQUEST, body = "Name to long")

    # If the name contains illegal character respond with 400 Bad Request
    if not re.fullmatch("[a-zA-Z0-9-]+", name):
        return TextResponse(status = HTTPStatus.BAD_REQUEST, body = "Invalid name")

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
@main.requires_json
def disconnect_worker(request: JSONRequest) -> TextResponse:

    # Get the JSON body
    body = request.body_dict

    # Get the worker UUID
    uuid = body.get("uuid")

    # If the worker uuid is missing respond with 400 Bad Request
    if not uuid:
        return TextResponse(status = HTTPStatus.BAD_REQUEST, body = "Missing UUID")

    # Try to parse the UUID
    try:
        uuid = UUID(uuid)

    # If the UUID is invalid respond with 400 Bad Request
    except ValueError:
        return TextResponse(status = HTTPStatus.BAD_REQUEST, body = "Invalid UUID")

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