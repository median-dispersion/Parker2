from wsgi import wsgi
from database import pool
import sys
from http import HTTPStatus
import re
import json
from uuid import UUID

# Set the main WSGI instance
main = wsgi

# =================================================================================================
# Initialization
# =================================================================================================
def initialize():

    # Terminate all workers that have not deregistered themselves
    with pool.connection() as connection:
        with connection.transaction():
            connection.execute("""
                UPDATE workers
                SET
                    state = 'terminated',
                    termination_date = now()
                WHERE state = 'registered';
            """)

# Run the initialization function if the initialization launch argument is provided
if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "initialize":
            initialize()

# =================================================================================================
# Worker registration
# =================================================================================================
@main.POST("/worker/registration")
@main.requires_json_body
def worker_registration(request: dict) -> dict:

    # Get the name of the worker
    name = request["body"].get("name")

    # If there is no name respond with 400 Bad Request
    if not name:
        return {
            "status": HTTPStatus.BAD_REQUEST,
            "body": "Missing name!"
        }

    # If the name is to short respond with 400 Bad Request
    if len(name) < 1:
        return {
            "status": HTTPStatus.BAD_REQUEST,
            "body": "Name to short"
        }

    # If the name is to long respond with 400 Bad request
    if len(name) > 64:
        return {
            "status": HTTPStatus.BAD_REQUEST,
            "body": "Name to long!"
        }

    # If the name contains any other characters than "a-z", "A-Z", "0-9" or "-" respond with 400 Bad Request
    if not re.fullmatch("[a-zA-Z0-9-]+", name):
        return {
            "status": HTTPStatus.BAD_REQUEST,
            "body": "Illegal character in name!"
        }

    # Insert the worker into the database
    with pool.connection() as connection:
        with connection.transaction():
            row = connection.execute(t"""
                INSERT INTO workers (name)
                VALUES ({name})
                RETURNING uuid;
            """).fetchone()

    # Return the worker UUID as JSON
    return {
        "status": HTTPStatus.OK,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "uuid": str(row["uuid"])
        })
    }

# =================================================================================================
# Worker deregistration
# =================================================================================================
@main.POST("/worker/deregistration")
@main.requires_json_body
def worker_deregistration(request: dict) -> dict | None:

    # Get the worker UUID
    uuid = request["body"].get("uuid")

    # If there is no UUID respond with 400 Bad Request
    if not uuid:
        return {
            "status": HTTPStatus.BAD_REQUEST,
            "body": "Missing UUID!"
        }

    # Try to parse the UUID
    try:
        uuid = UUID(uuid)

    # If the UUID is invalid respond with 400 Bad Request
    except ValueError:
        return {
            "status": HTTPStatus.BAD_REQUEST,
            "body": "Invalid UUID!"
        }

    # Update the worker in the database
    with pool.connection() as connection:
        with connection.transaction():
            cursor = connection.execute(t"""
                UPDATE workers
                SET
                    state = 'deregistered',
                    deregistration_date = now()
                WHERE uuid = {uuid}
                AND state = 'registered';
            """)

    # If no rows where affected, meaning no registered worker was found, respond with 400 Bad Request
    if cursor.rowcount == 0:
        return {
            "status": HTTPStatus.BAD_REQUEST,
            "body": "No registered worker with the given UUID!"
        }

    # Respond with 200 OK
    return