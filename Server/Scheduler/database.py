from psycopg_pool import ConnectionPool
import os
from psycopg.rows import dict_row
import atexit

# Create a new database connection pool
pool = ConnectionPool(

    # Connection parameters
    kwargs={

        # PostgreSQL settings
        "host": os.getenv("POSTGRES_HOST", "0.0.0.0"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "user": os.getenv("POSTGRES_USER", "user"),
        "password": os.getenv("POSTGRES_PASSWORD", "password"),
        "dbname": os.getenv("POSTGRES_DB", "database"),

        # Make all queries persisted immediately, unless explicitly using a transaction block
        "autocommit": True,

        # Return rows as dictionaries
        "row_factory": dict_row

    },

    # Limit the number of connections in the pool to one
    # This is because the application will be running multiprocessed through gunicorn
    # Each process is handling 1 request at a time and each request requires just one connection
    # The pool is used for connection management, automatically closing broken ones and acquiring new connections
    # Example: gunicorn > spawns 4 workers > each worker has 1 connection to the database through the pool
    min_size=1,
    max_size=1,

    # Immediately open the connection when the pool is initialized
    open=True,

    # Check if the connection is working before yielding it, otherwise create a new connection
    check=ConnectionPool.check_connection

)

# Wait for the pool to be ready or raise an exception after the default timeout
pool.wait()

# Close the pool on exit
atexit.register(pool.close)