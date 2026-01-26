from fastapi import FastAPI, Depends, HTTPException
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from pydantic import constr
from sqlalchemy import text

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