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
    def __init__(self, thread_id: int, *args, **kwargs):

        # Initialize member variables
        self._thread_id = thread_id
        self._worker_name = f"{settings.worker_name}-{self._thread_id}"
        self._logger = logging.getLogger(self._worker_name)
        self._stop_event = threading.Event()
        self._session: Session | None = None
        self._worker_uuid: UUID | None  = None

        # Re-check the worker name length and raise an exception if it is too long
        if len(self._worker_name) > 64:
            raise ValueError("Worker name too long")

        # Call the parent constructor
        super().__init__(*args, **kwargs)

    # =============================================================================================
    # Connect to the manager
    # =============================================================================================
    def _connect(self):

        # Connection URL
        url = f"{settings.manager_url}/worker/connect"

        # Required JSON data
        json = {"name": self._worker_name}

        # Connect to the manager
        response = self._session.post(url = url, json = json)

        # Set the worker UUID
        self._worker_uuid = UUID(response.json()["uuid"])

    # =============================================================================================
    # Disconnect from the manager
    # =============================================================================================
    def _disconnect(self):

        # Disconnection URL
        url = f"{settings.manager_url}/worker/disconnect"

        # Required JSON data
        json = {"uuid": str(self._worker_uuid)}

        # Disconnect from the manager
        response = self._session.post(url = url, json = json)

    # =============================================================================================
    # Main worker loop
    # =============================================================================================
    def run(self):

        # Log that the worker has started
        self._logger.info("Started")

        # Loop until stopped
        while not self._stop_event.is_set():

            # Exception handler
            try:

                # Get a request session
                self._session = Session()

                # Connect to the manager
                self._connect()

                # Loop until stopped
                while not self._stop_event.is_set():
                    self._stop_event.wait(1)

                # Disconnect from the manager
                self._disconnect()

            # Log any unhandled exception and then continue
            except:
                self._logger.exception("Unhandled exception occurred")

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