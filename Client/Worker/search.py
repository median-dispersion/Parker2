import threading
import sys
import subprocess
import settings
import json

# =================================================================================================
# Search class
# =================================================================================================
class Search(threading.Thread):

    # =============================================================================================
    # Initialization
    # =============================================================================================
    def __init__(self, start_index: int, end_index: int):

        # Raise an exception if the start index is not an integer
        if not isinstance(start_index, int):
            raise TypeError("Start index must be an integer")

        # Raise an exception if the end index is not an integer
        if not isinstance(end_index, int):
            raise TypeError("End index must be an integer")

        # Raise an exception if the start index is too small
        if start_index < 0:
            raise ValueError("Start index too small")

        # Raise an exception if the end index is too small
        if end_index < start_index:
            raise ValueError("End index too small")

        # Raise an exception if the end index is too big
        if end_index > 18446744073709551615:
            raise ValueError("End index too big")

        # Call the parent constructor
        super().__init__()

        # Initialize member variables
        self._start_index = start_index
        self._end_index = end_index
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._done_event = threading.Event()
        self._exception: BaseException | None = None
        self._process: subprocess.Popen | None = None
        self._received_initialization = False
        self._received_result = False
        self._current_index = start_index
        self._solutions_found = 0
        self._solutions: list[dict[str, int]] | list = []
        self._total_runtime_seconds: float | None = None
        self._finished = False

    # =============================================================================================
    # Main search thread
    # =============================================================================================
    def run(self):

        try:

            # Return immediately if the stop event is set
            if self._stop_event.is_set():
                return

            # Start the search process
            self._process = subprocess.Popen(
                [
                    str(settings.search_binary),
                    str(self._start_index),
                    str(self._end_index)
                ],
                process_group = 0,       # Give it its own process group, for signal handling
                stdout = subprocess.PIPE # Capture the output stream as bytes
            )

            # Check if the stop event was set while the process was started
            # Stop the search process immediately by returning
            if self._stop_event.is_set():
                return

            # Loop until there is not more data in the output stream
            while True:

                # Read one line or a maximum of 1 MB from the output stream
                line = self._process.stdout.readline(1_048_576)

                # Break the loop if the output stream returned no more data
                if not line:
                    break

                # Check if the read was cut short because the search process was stopped
                # In that case return immediately
                if self._stop_event.is_set():
                    return

                # Decode the line as JSON
                data = json.loads(line)

                # The first data received from the search process must be the initialization
                if not self._received_initialization:

                    # Raise an exception if the search process initialization failed
                    if (
                        str(data["type"]) != "initialization"
                        or
                        int(data["start_index"]) != self._start_index
                        or
                        int(data["end_index"]) != self._end_index
                    ):
                        raise RuntimeError("Search process initialization failed")

                    # Else set the the received initialization flag and continue
                    self._received_initialization = True
                    continue

                # Raise an exception if the search result was already sent but more data was received
                if self._received_result:
                    raise RuntimeError("Already received the search result")

                # Match the data type
                match str(data["type"]):

                    # Update the search values
                    case "update":
                        with self._lock:
                            self._current_index = int(data["current_index"])
                            self._solutions_found = int(data["solutions_found"])

                    # Add a solution
                    case "solution":
                        with self._lock:
                            self._solutions.append({
                                "a": int(data["a"]), "b": int(data["b"]), "c": int(data["c"]),
                                "d": int(data["d"]), "e": int(data["e"]), "f": int(data["f"]),
                                "g": int(data["g"]), "h": int(data["h"]), "i": int(data["i"])
                            })

                    # Finalize the search values
                    case "result":
                        with self._lock:
                            self._total_runtime_seconds = float(data["total_runtime_seconds"])
                            self._solutions_found = int(data["solutions_found"])
                            self._current_index = self._end_index
                            self._received_result = True

                    # Raise an exception if the data type is unexpected
                    case _:
                        raise RuntimeError("Received unexpected data type")

            # Wait until the search process returns and get its return code
            return_code = self._process.wait()

            # Check if the search process returned because a stop was requested
            # Return immediately if the stop event is set
            if self._stop_event.is_set():
                return

            # Raise an exception if the return code is non zero
            if return_code != 0:
                raise RuntimeError(f"Return code {return_code}")

            # Raise an exception if the search result was never received
            if not self._received_result:
                raise RuntimeError("Received no search result")

            # Raise and exception if the number of received and found solutions don't match
            if len(self._solutions) != self._solutions_found:
                raise RuntimeError("Number of received and found solutions don't match")

            # Set the finished flag
            with self._lock:
                self._finished = True

        # Catch and store any unhandled exception
        except:
            with self._lock:
                self._exception = sys.exception()

        # Cleanup
        finally:

            # Ensure the search process is stopped
            # In very rare cases killing the process might raise an exception
            # This could leave a zombie / orphan process
            # But if the kill fails there is nothing that can really be done about that
            # Except closing stdout, witch might make the search process crash on the next update
            try:
                if self._process is not None:
                    try:
                        self._process.kill()
                        self._process.wait()
                    finally:
                        self._process.stdout.close()

            # Catch and store the exception if there was no previous exception
            except:
                with self._lock:
                    if self._exception is None:
                        self._exception = sys.exception()

            # Set the done event
            finally:
                self._done_event.set()

    # =============================================================================================
    # Stop the search thread
    # =============================================================================================
    def stop(self):

        # Set the stop event
        self._stop_event.set()

        # Stop the search process
        if self._process is not None:
            self._process.kill()

    # =============================================================================================
    # Wait for the specified amount of time or until the search is done
    # =============================================================================================
    def wait(self, timeout_seconds: float | None = None):
        return self._done_event.wait(timeout = timeout_seconds)

    # =============================================================================================
    # Get the done flag
    # =============================================================================================
    @property
    def done(self) -> bool:
        return self._done_event.is_set()

    # =============================================================================================
    # Get the current search index
    # =============================================================================================
    @property
    def current_index(self) -> int:
        with self._lock:
            return self._current_index

    # =============================================================================================
    # Get the number of found solutions
    # =============================================================================================
    @property
    def solutions_found(self) -> int:
        with self._lock:
            return self._solutions_found

    # =============================================================================================
    # Get the exception
    # =============================================================================================
    @property
    def exception(self) -> BaseException | None:
        with self._lock:
            return self._exception

    # =============================================================================================
    # Get the finished flag
    # =============================================================================================
    @property
    def finished(self) -> bool:
        with self._lock:
            return self._finished

    # =============================================================================================
    # Get the solutions, may only be read when the finish flag has been set
    # =============================================================================================
    @property
    def solutions(self) -> list[dict[str, int]] | list:
        with self._lock:
            return self._solutions

    # =============================================================================================
    # Get the total runtime in second, may only be read when the finish flag has been set
    # =============================================================================================
    @property
    def total_runtime_seconds(self) -> float | None:
        with self._lock:
            return self._total_runtime_seconds