import threading
import settings
import logging
from session import Session
from uuid import UUID
from typing import Any

# =================================================================================================
# Worker class
# =================================================================================================
class Worker(threading.Thread):

    # =============================================================================================
    # Initialization
    # =============================================================================================
    def __init__(self, thread_index: int):

        # Call the parent constructor
        super().__init__()

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
        self._job: dict[str, Any] | None = None

    # =============================================================================================
    # Reset the worker to its initial state
    # =============================================================================================
    def _reset(self):
        self._session = None
        self._uuid = None
        self._job = None

    # =============================================================================================
    # Connect to the manager
    # =============================================================================================
    def _connect(self):

        # Request URL
        url = f"{settings.manager_url}/worker/connect"

        # Request body
        body = {"name": self._name}

        # Connect to the manager
        worker = self._session.post(url = url, json = body).json()

        # Set the worker UUID
        self._uuid = UUID(worker["uuid"])

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
    # Get the latest job rules from the manager
    # =============================================================================================
    def _get_job_rules(self) -> dict[str, int]:

        # Get the latest job rules from the manager
        job_rules = self._session.get(f"{settings.manager_url}/job/rules").json()

        # Ensure all required arguments are present and of the correct type
        job_rules["minimum_size"] = int(job_rules["minimum_size"])
        job_rules["maximum_size"] = int(job_rules["maximum_size"])
        job_rules["target_duration_seconds"] = int(job_rules["target_duration_seconds"])
        job_rules["update_interval_seconds"] = int(job_rules["update_interval_seconds"])

        # Return the job rules
        return job_rules

    # =============================================================================================
    # Claim a job from the manager
    # =============================================================================================
    def _claim_job(self, size: int):

        # Request URL
        url = f"{settings.manager_url}/job/claim"

        # Request body
        body = {
            "worker_uuid": str(self._uuid),
            "size": size
        }

        # Claim a job
        job = self._session.post(url = url, json = body).json()

        # Ensure all required arguments are present and of the correct type
        job["uuid"] = UUID(job["uuid"])
        job["attempt"] = int(job["attempt"])
        job["start_index"] = int(job["start_index"])
        job["end_index"] = int(job["end_index"])

        # Set the current job
        self._job = job

    # =============================================================================================
    # Send a job update to the manager
    # =============================================================================================
    def _update_job(self, current_index: int, solutions_found: int):

        # Request URL
        url = f"{settings.manager_url}/job/update"

        # Request body
        body = {
            "uuid": str(self._job["uuid"]),
            "attempt": self._job["attempt"],
            "worker_uuid": str(self._uuid),
            "current_index": current_index,
            "solutions_found": solutions_found
        }

        # Update the job
        self._session.post(url = url, json = body)

    # =============================================================================================
    # Send a job cancellation to the manager
    # =============================================================================================
    def _cancel_job(self, cancellation_reason: str):

        # Request URL
        url = f"{settings.manager_url}/job/cancel"

        # Request body
        body = {
            "uuid": str(self._job["uuid"]),
            "attempt": self._job["attempt"],
            "cancellation_reason": cancellation_reason,
            "worker_uuid": str(self._uuid)
        }

        # Cancel the job
        self._session.post(url = url, json = body)

        # Clear the job
        self._job = None

    # =============================================================================================
    # Send a finished job to the manager
    # =============================================================================================
    def _finish_job(self, total_runtime_seconds: float, solutions_found: int):

        # Request URL
        url = f"{settings.manager_url}/job/finish"

        # Request body
        body = {
            "uuid": str(self._job["uuid"]),
            "attempt": self._job["attempt"],
            "worker_uuid": str(self._uuid),
            "total_runtime_seconds": total_runtime_seconds,
            "solutions_found": solutions_found
        }

        # Finish the job
        self._session.post(url = url, json = body)

        # Clear the job
        self._job = None

    # =============================================================================================
    # Submit a solution to the manager
    # =============================================================================================
    def _submit_solution(self, solution: dict[str, int]):

        # Request URL
        url = f"{settings.manager_url}/solution/submit"

        # Request body
        body = {
            "worker_uuid": str(self._uuid),
            "job_uuid": str(self._job["uuid"])
        }

        # Update the request body by adding the solution
        body.update(solution)

        # Submit the solution
        self._session.post(url = url, json = body)

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
                if self._uuid is not None:
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