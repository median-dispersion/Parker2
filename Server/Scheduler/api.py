from fastapi import FastAPI, Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session

# Initialize FastAPI
api = FastAPI()

# Create the database session dependency
session_dependency = Annotated[AsyncSession, Depends(get_session)]