from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from settings import settings
from sqlalchemy import text

# Initialize SQLAlchemy engine and session
engine = create_async_engine(settings.sqlalchemy_url)
session = async_sessionmaker(engine)

# =================================================================================================
# Get a database session
# =================================================================================================
async def get_session() -> AsyncSession:

    # Get the database session
    async with session() as database_session:

        # Yield the database session
        yield database_session

# =================================================================================================
# Database initialization routine
# =================================================================================================
async def initialization():

    # Get the database session
    async with session() as database_session:

        # A flag for checking if a new row was inserted
        inserted = False

        # Loop until a new row is inserted or hang at the initialization process
        # This is to make sure the database is properly set up
        # If it is not simply never continue
        while not inserted:

            try:

                # Insert a new search row when the scheduler starts up
                # The start, next and end index will be set to the end index of the last search
                # Or to 0 if no previous search was conducted
                await database_session.execute(text("""
                    INSERT INTO searches (
                        start_index,
                        next_index,
                        end_index
                    )
                    SELECT
                        COALESCE(last_search.end_index, 0) AS start_index,
                        COALESCE(last_search.end_index, 0) AS next_index,
                        COALESCE(last_search.end_index, 0) AS end_index
                    FROM (
                        SELECT end_index
                        FROM searches
                        WHERE end_date IS NOT NULL
                        ORDER BY id DESC
                        LIMIT 1
                    ) AS last_search
                    RIGHT JOIN (SELECT 1) AS dummy_row ON true;
                """))

                # Commit changes to database
                await database_session.commit()

                # Set the inserted flag to true and stop looping
                inserted = True

            # Exception for if no row was inserted
            # This could be caused by the unlikely event of a generated UUID not being unique
            # Or some unhandled exception at initialization time
            except Exception:

                # Rollback changes and try again by looping
                await database_session.rollback()

# =================================================================================================
# Database cleanup routine
# =================================================================================================
async def cleanup():

    # Get the database session
    async with session() as database_session:

        try:

            # Set the end date of latest search
            await database_session.execute(text("""
                UPDATE searches
                SET end_date = now()
                WHERE id = (
                    SELECT id
                    FROM searches
                    WHERE end_date IS NULL
                    ORDER BY id DESC
                    LIMIT 1
                );
            """))

            # Commit changes to database
            await database_session.commit()

        # If an exception occurs
        except Exception:

            # Rollback database changes
            await database_session.rollback()