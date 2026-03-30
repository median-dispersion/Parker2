import threading
from settings import settings
import requests
from uuid import UUID
from search import Search

class Client(threading.Thread):

    # =============================================================================================
    # Constructor
    # =============================================================================================
    def __init__(
        self,
        name: str
    ) -> None:

        # Call the parent constructor
        super().__init__()

        # Initialize members
        self._name = name
        self._stop_event = threading.Event()
        self._uuid = None
        self._next_job_size = 1
        self._job = {
            "uuid": None,
            "start_index": None,
            "current_index": None,
            "end_index": None,
            "update_seconds": None,
            "results": []
        }
        self._search_thread = None

    # =============================================================================================
    # Perform a request
    # =============================================================================================
    def _request(
        self,
        method: str,
        url: str,
        body: str
    ) -> dict | None:

        # Number of request attempts
        attempt = 0

        # Loop while not stopped, until a request is successful or the maximum number of attempts is reached
        while not self._stop_event.is_set() and attempt < settings.request_attempts:

            # Increase the number of request attempts
            attempt += 1

            try:

                # Perform the request
                response = requests.request(
                    method=method.upper(),
                    url=url,
                    json=body,
                    timeout=settings.request_timeout_seconds
                )

                # Raise exception for HTTP errors (4xx, 5xx)
                response.raise_for_status()

                # Return the parsed JSON data
                return response.json()

            # If th request fails
            except Exception as exception:

                # Print the exception
                print(f"{self._name}: {exception}")

                # Delay the next request attempt
                self._stop_event.wait(timeout=settings.request_attempt_delay_seconds)

        # Raise an exception if the maximum number of request attempts was reached
        if (attempt >= settings.request_attempts):
            raise RuntimeError("Maximum number of request attempts was reached!")

    # =============================================================================================
    # Register the client
    # =============================================================================================
    def _register_client(self) -> None:

        # Construct request URL
        url = f"{settings.server_url}/client/register"

        # Construct request body
        body = {"client_name": self._name}

        # Perform request
        data = self._request("POST", url, body)

        # Parse and set the client UUID
        self._uuid = UUID(data["uuid"])

    # =============================================================================================
    # Claim a job from the server
    # =============================================================================================
    def _claim_job(self) -> None:

        # Construct request URL
        url = f"{settings.server_url}/job/claim"

        # Construct request body
        body = {
            "client_uuid": str(self._uuid),
            "job_size": self._next_job_size
        }

        # Perform request
        data = self._request("POST", url, body)

        # Parse and set the job data
        self._job["uuid"] = UUID(data["uuid"])
        self._job["start_index"] = int(data["start_index"])
        self._job["current_index"] = int(data["start_index"])
        self._job["end_index"] = int(data["end_index"])
        self._job["update_seconds"] = int(data["update_seconds"])

    # =============================================================================================
    # Start the search thread
    # =============================================================================================
    def _start_search(self) -> None:

        # Initialize the search thread
        self._search_thread = Search(
            f"{self._name}-Search",
            self._job["start_index"],
            self._job["end_index"]
        )

        # Start the search
        self._search_thread.start()

    # =============================================================================================
    # Send a job update to the server
    # =============================================================================================
    def _update_job(self) -> None:

        # Construct request URL
        url = f"{settings.server_url}/job/update"

        # Construct request body
        body = {
            "client_uuid": str(self._uuid),
            "job_uuid": str(self._job["uuid"]),
            "current_job_index": self._job["current_index"]
        }

        # Perform request
        self._request("POST", url, body)

    # =============================================================================================
    # Send the job completion to the server
    # =============================================================================================
    def _complete_job(self) -> None:

        # Construct request URL
        url = f"{settings.server_url}/job/complete"

        # Construct request body
        body = {
            "client_uuid": str(self._uuid),
            "job_uuid": str(self._job["uuid"])
        }

        # Perform request
        self._request("POST", url, body)

    # =============================================================================================
    # Submit results to the server
    # =============================================================================================
    def _submit_results(self) -> None:

        # Construct request URL
        url = f"{settings.server_url}/result/submit"

        # Loop through every result
        for result in self._job["results"]:

            # Construct request body
            body = {
                "client_uuid": str(self._uuid),
                "job_uuid": str(self._job["uuid"]),
                "a": result["a"],
                "b": result["b"],
                "c": result["c"],
                "d": result["d"],
                "e": result["e"],
                "f": result["f"],
                "g": result["g"],
                "h": result["h"],
                "i": result["i"]
            }

            # Perform request
            self._request("POST", url, body)

    # =============================================================================================
    # Run the client
    # =============================================================================================
    def run(self) -> None:

        # Loop until stopped
        while not self._stop_event.is_set():

            try:

                # Register the client
                self._register_client()

                 # Loop until stopped
                while not self._stop_event.is_set():

                    # Claim a job
                    self._claim_job()

                    # Start the search
                    self._start_search()

                    # Loop as long as the search is running
                    while self._search_thread.is_alive():

                        # Update the current index
                        self._job["current_index"] = self._search_thread.current_index

                        # Update the job
                        self._update_job()

                        # Wait until the next job update or the search thread end
                        self._search_thread.wait(self._job["update_seconds"])

                    # Get the search results
                    self._job["results"] = self._search_thread.results

                    # Submit the results
                    self._submit_results()

                    # Check if the search didn't completed
                    if not self._search_thread.completed:

                        # Raise an exception
                        raise RuntimeError("Search did not complete!")

                    # Complete the job
                    self._complete_job()

                    # Get the job size of the completed job
                    job_size = self._job["end_index"] - self._job["start_index"]

                    # Calculate the search iterations per second
                    iterations_per_second = job_size / self._search_thread.execution_time

                    # Scale the next job size accordingly
                    self._next_job_size = max(round(iterations_per_second * settings.search_duration_seconds), 1)

            # If any of the steps fail
            except Exception as exception:

                # Reset the next jobs size
                self._next_job_size = 1

                # Print the exception and try again, from the start
                print(f"{self._name}: {exception}")

    # =============================================================================================
    # Stop the client
    # =============================================================================================
    def stop(self) -> None:

        # Check if the search thread is set
        if self._search_thread is not None:

            # Stop the search thread
            self._search_thread.stop()

        # Set the stop event
        self._stop_event.set()

    # =============================================================================================
    # Return the client name
    # =============================================================================================
    @property
    def name(self) -> str:
        return self._name