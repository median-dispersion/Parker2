import threading
import time
import subprocess
from settings import settings
import json

class Search(threading.Thread):

    # =============================================================================================
    # Constructor
    # =============================================================================================
    def __init__(
        self,
        name: str,
        start_index: int,
        end_index: int
    ) -> None:

        # Call the parent constructor
        super().__init__()

        # Initialize members
        self._name = name
        self._start_index = start_index
        self._current_index = start_index
        self._end_index = end_index
        self._lock = threading.Lock()
        self._process = None
        self._results = []
        self._start_time = time.time()
        self._execution_time = None
        self._completed = False

    # =============================================================================================
    # Run the search
    # =============================================================================================
    def run(self) -> None:

        # Capture start time
        self._start_time = time.time()

        try:

            # Start the search process
            self._process = subprocess.Popen(
                [
                    str(settings.search_binary_path),
                    str(self._start_index),
                    str(self._end_index)
                ],
                stdout=subprocess.PIPE, # Capture output
                stderr=subprocess.PIPE, # Capture errors
                text=True,              # Output text instead of bytes
                bufsize=1               # Line buffered
            )

            # Read output line by line
            for line in self._process.stdout:

                # Parse the output line as JSON
                data = json.loads(line.strip())

                # If data contains the current index set it
                if "current_index" in data:
                    with self._lock:
                        self._current_index = data["current_index"]

                # If data contains a result append it
                if "result" in data:
                    with self._lock:
                        self._results.append(data["result"])

            # Wait for the search process to finish
            self._process.wait()

            # Only set the completed flag to true if the search exited without errors
            if self._process.returncode == 0:
                with self._lock:
                    self._completed = True

        # If an unhandled exception occurs
        except Exception as exception:

            # Stop the search process immediately
            self.stop()

            # Print the exception
            print(f"{self._name}: {exception}")

        # Capture the execution time
        with self._lock:
            self._execution_time = time.time() - self._start_time

    # =============================================================================================
    # Stop the search
    # =============================================================================================
    def stop(self) -> None:

        # Check if the search process is set
        if self._process is not None:

            # Kill the search process
            self._process.kill()

    # =============================================================================================
    # Get the current index
    # =============================================================================================
    @property
    def current_index(self) -> int:
        with self._lock:
            return self._current_index

    # =============================================================================================
    # Get the results list
    # =============================================================================================
    @property
    def results(self) -> list:

        # Acquire the thread lock
        with self._lock:

            # Return a copy of the results
            return self._results.copy()

    # =============================================================================================
    # Get the completion state
    # =============================================================================================
    @property
    def completed(self) -> bool:
        with self._lock:
            return self._completed

    # =============================================================================================
    # Get the execution time
    # =============================================================================================
    @property
    def execution_time(self) -> float:

        # Acquire the thread lock
        with self._lock:

            # Get the final execution time
            execution_time = self._execution_time

        # If the final execution time is none
        if execution_time is None:

            # Calculate the execution time so far
            execution_time = time.time() - self._start_time

        # Return the execution time
        return execution_time