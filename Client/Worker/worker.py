import threading
import settings
import logging
from session import Session
from uuid import UUID

# =================================================================================================
# Worker class
# =================================================================================================
class Worker(threading.Thread):

    # =============================================================================================
    # Initialization
    # =============================================================================================
    def __init__(self, thread_index: int, *args, **kwargs):

        # Call the parent constructor
        super().__init__(*args, **kwargs)

        # Set the worker name
        self._name = f"{settings.worker_name}-{thread_index}"

        # Re-check the worker name length and raise an exception if it is too long
        if len(self._name) > 64:
            raise ValueError("Worker name too long")

        # Initialize member variables
        self._logger = logging.getLogger(self._name)
        self._stop_event = threading.Event()
        self._session: Session | None = None
        self._uuid: UUID | None  = None

    # =============================================================================================
    # Reset the worker to its initial state
    # =============================================================================================
    def _reset(self):
        self._session = None
        self._uuid = None

    # =============================================================================================
    # Connect to the manager
    # =============================================================================================
    def _connect(self):

        # Request URL
        url = f"{settings.manager_url}/worker/connect"

        # Request body
        body = {"name": self._name}

        # Connect to the manager
        response = self._session.post(url = url, json = body).json()

        # Set the worker UUID
        self._uuid = UUID(response["uuid"])

    # =============================================================================================
    # Disconnect from the manager
    # =============================================================================================
    def _disconnect(self):

        # Request URL
        url = f"{settings.manager_url}/worker/disconnect"

        # Request body
        body = {"uuid": str(self._uuid)}

        # Disconnect from the manager
        self._session.post(url = url, json = body)

        # Clear the worker UUID
        self._uuid = None

    # =============================================================================================
    # Main worker loop
    # =============================================================================================
    def run(self):

        # Log that the worker has started
        self._logger.info("Started")

        # Loop until stopped
        while not self._stop_event.is_set():

            try:

                # Reset the worker to its initial state
                self._reset()

                # Get a request session
                self._session = Session()

                # Connect to the manager
                self._connect()

                # Loop until stopped
                while not self._stop_event.is_set():
                    self._stop_event.wait(1)

                # Disconnect from the manager
                self._disconnect()

            # Catch any unhandled exceptions
            except:

                # Log the exception
                self._logger.exception("Unhandled exception")

                # If the worker is still connected try to disconnect it
                # If the disconnect fails, log it and continue
                if self._uuid != None:
                    try:
                        self._disconnect()
                    except:
                        self._logger.exception("Failed to disconnect after exception")

        # Log that the worker has stopped
        self._logger.info("Stopped")

    # =============================================================================================
    # Stop the worker
    # =============================================================================================
    def stop(self):

        # Log the stop event
        self._logger.info("Stopping...")

        # Set the stop event
        self._stop_event.set()