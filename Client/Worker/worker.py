import threading
import settings
import logging
from session import Session
from uuid import UUID
from typing import Any
from search import Search
from traceback import format_exc

# =================================================================================================
# Worker class
# =================================================================================================
class Worker(threading.Thread):

    # =============================================================================================
    # Initialization
    # =============================================================================================
    def __init__(self, thread_index: int):

        # Construct the worker name
        name = f"{settings.worker_name}-{thread_index}"

        # Re-check the worker name length and raise an exception if it is too long
        if len(name) > 64:
            raise ValueError("Worker name too long")

        # Call the parent constructor
        super().__init__(name = name)

        # Initialize member variables
        self._logger = logging.getLogger(self.name)
        self._stop_event = threading.Event()
        self._session: Session | None = None
        self._uuid: UUID | None  = None
        self._job: dict[str, Any] | None = None
        self._search: Search | None = None

    # =============================================================================================
    # Reset the worker to its initial state
    # =============================================================================================
    def _reset(self):
        self._session = None
        self._uuid = None
        self._job = None
        self._search = None

    # =============================================================================================
    # Connect to the manager
    # =============================================================================================
    def _connect(self):

        # Request URL
        url = f"{settings.manager_url}/worker/connect"

        # Request body
        body = {"name": self.name}

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

        # The data received from the manager should be trustworthy
        # But a misconfigured manager could cause some hot loops in the worker
        # This is why there are some basic validations that will raise on misconfigured values

        if job_rules["minimum_size"] < 0:
            raise ValueError("Minimum job size too small")

        if job_rules["maximum_size"] < job_rules["minimum_size"]:
            raise ValueError("Maximum job size too small")

        if job_rules["maximum_size"] > 18446744073709551615:
            raise ValueError("Maximum job size too big")

        if job_rules["target_duration_seconds"] < 0:
            raise ValueError("Target job duration too small")

        if job_rules["update_interval_seconds"] < 0:
            raise ValueError("Job update interval too small")

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

        # The data received from the manager should be trustworthy
        # But a misconfigured manager could cause some hot loops in the worker
        # This is why there are some basic validations that will raise on misconfigured values

        if job["attempt"] < 1:
            raise ValueError("Invalid job attempt")

        if job["start_index"] < 0:
            raise ValueError("Job start index too small")

        if job["end_index"] < job["start_index"]:
            raise ValueError("Job end index too small")

        if job["end_index"] > 18446744073709551615:
            raise ValueError("Job end index too big")

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
    # Get the next job size
    # =============================================================================================
    def _get_next_job_size(self, total_runtime_seconds: float, target_duration_seconds: int):

        # Get the size of the finished job
        finished_job_size = self._job["end_index"] - self._job["start_index"]

        # Calculate the iterations per second
        iterations_per_second = finished_job_size / total_runtime_seconds

        # Calculate the next job size using linear approximation
        # This is not very accurate but good enough as long as the manger provides decent job rules
        next_job_size = iterations_per_second * target_duration_seconds

        # Convert the next job size to an integer and limit it to a minimum of 1
        # The real next job size will also be clamped in accordance with the job rules from the manager
        next_job_size = max(int(round(next_job_size)), 1)

        # Return the next job size
        return next_job_size

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

                # Log event
                self._logger.debug(f"Connected as {self._uuid}")

                # Initialize the next job size
                next_job_size = 1

                # Loop until stopped
                while not self._stop_event.is_set():

                    # Get the latest job rules
                    job_rules = self._get_job_rules()

                    # Clamp the next job size in accordance with the job rules
                    next_job_size = max(job_rules["minimum_size"], min(next_job_size, job_rules["maximum_size"]))

                    # Claim a job
                    self._claim_job(next_job_size)

                    # Log event
                    self._logger.debug(f"Claimed job {self._job['uuid']}")

                    # Initialize the search thread
                    self._search = Search(self._job["start_index"], self._job["end_index"])

                    # Break the loop if the stop event was set while the search thread was initialized
                    if self._stop_event.is_set():
                        break

                    # Start the search thread
                    self._search.start()

                    # Log event
                    self._logger.debug(f"Started search from {self._job['start_index']} to {self._job['end_index']}")

                    # Loop until the search is done
                    while not self._search.done:

                        # Update the job with the latest search values
                        self._update_job(self._search.current_index, self._search.solutions_found)

                        # Log event
                        self._logger.debug(f"Updated job {self._job['uuid']}")

                        # Delay the next job update for the amount of time set by the job rules
                        # Or until the search thread is done
                        self._search.wait(job_rules["update_interval_seconds"])

                    # Wait for the search thread to join
                    self._search.join()

                    # Re-raise any exception that might have occurred in the search thread
                    if self._search.exception is not None:
                        raise self._search.exception

                    # Check if the search finished successfully
                    if self._search.finished:

                        # Log event
                        self._logger.debug("Finished search")

                        # Submit all solutions found by the search
                        for solution in self._search.solutions:
                            self._submit_solution(solution)
                            self._logger.debug(f"Submitted solution {solution}")

                        # Get the next job size
                        next_job_size = self._get_next_job_size(self._search.total_runtime_seconds, job_rules["target_duration_seconds"])

                        # Finish the job
                        self._finish_job(self._search.total_runtime_seconds, self._search.solutions_found)

                        # Log event
                        self._logger.debug("Finished job")

                    # Raise an exception if the search never finished
                    elif not self._stop_event.is_set():
                        raise RuntimeError("Search ended without finishing")

                # Cancel the job if it is still claimed
                if self._job is not None:
                    self._cancel_job("Worker shutdown")

                # Log event
                self._logger.debug("Canceled job")

                # Disconnect from the manager
                self._disconnect()

                # Log event
                self._logger.debug("Disconnected")

            # Catch any unhandled exceptions
            except:

                # Get the formatted exception
                formatted_exception = format_exc()

                # Log the exception
                self._logger.exception("Unhandled exception")

                # If the search is still running try to stop it
                # If that fails, log it and continue
                if self._search is not None:
                    try:
                        self._search.stop()
                        self._search.join()
                    except:
                        self._logger.exception("Failed to stop search after exception")

                # If the job is still claimed try to cancel it
                # If that fails, log it and continue
                if self._job is not None:
                    try:
                        self._cancel_job(formatted_exception)
                    except:
                        self._logger.exception("Failed to cancel job after exception")

                # If the worker is still connected try to disconnect it
                # If that fails, log it and continue
                if self._uuid is not None:
                    try:
                        self._disconnect()
                    except:
                        self._logger.exception("Failed to disconnect after exception")

                # Delay the next attempt by 5 seconds
                self._stop_event.wait(5)

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

        # Get a local reference to the search thread
        search = self._search

        # Stop the search thread
        if search is not None:
            search.stop()