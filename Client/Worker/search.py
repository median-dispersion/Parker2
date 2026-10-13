import threading
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
    def __init__(
        self,
        start_index: int,
        end_index: int,
        *args,
        **kwargs
    ):

        # Call the parent constructor
        super().__init__(*args, **kwargs)

        # Raise an exception if the start index is too small
        if start_index < 0:
            raise ValueError("Start index too small")

        # Raise an exception if the end index is too small
        if end_index < start_index:
            raise ValueError("End index too small")

        # Raise an exception if the end index is too big
        if end_index > 18446744073709551615:
            raise ValueError("End index too big")

        # Initialize member variables
        self._start_index = start_index
        self._end_index = end_index
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._process: subprocess.Popen | None = None
        self._current_index = start_index
        self._solutions_found = 0
        self._solutions: list[dict[str, int]] | list = []
        self._received_result = False
        self._total_runtime_seconds: float | None = None
        self._finished = False

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
    # Get the received solutions
    # =============================================================================================
    @property
    def solutions(self) -> list[dict[str, int]] | list:
        with self._lock:
            return self._solutions.copy()

    # =============================================================================================
    # Get the total runtime in seconds
    # =============================================================================================
    @property
    def total_runtime_seconds(self) -> float | None:
        with self._lock:
            return self._total_runtime_seconds

    # =============================================================================================
    # Get the finished flag
    # =============================================================================================
    @property
    def finished(self) -> bool:
        with self._lock:
            return self._finished

    # =============================================================================================
    # Get the stopped flag
    # =============================================================================================
    @property
    def stopped(self) -> bool:
        return self._stop_event.is_set()

    # =============================================================================================
    # Main search thread
    # =============================================================================================
    def run(self):

        # Raise an exception if the stop event is set
        if self._stop_event.is_set():
            raise RuntimeError("Stop event is set")

        try:

            # Start the search process
            # Capture the output streams as text
            # Because not reading one of the output streams could lead to a deadlock
            # Both streams are merged and read out together line by line
            # If a line is decodable as JSON it is assumed to be from stdout
            # If a line is not decodable as JSON it is assumed to be from stderr
            # Lines from stderr are added to the output buffer up to the maximum buffer length
            self._process = subprocess.Popen(
                [
                    str(settings.search_binary),
                    str(self._start_index),
                    str(self._end_index)
                ],
                stdout = subprocess.PIPE,   # Capture the output stream
                stderr = subprocess.STDOUT, # Merge the error stream into the output stream
                text = True                 # Capture the output stream as text
            )

            # Maximum length of the output buffer
            # Around 8 MB, depending on the characters in the output stream
            maximum_buffer_length = 8_388_608

            # Current length of the output buffer
            buffer_length = 0

            # Output buffer
            buffer = []

            # Loop until there is no more data in the output stream
            while True:

                # Read one line or the maximum buffer length from the output stream
                line = self._process.stdout.readline(maximum_buffer_length)

                # Break the loop if there is no more data in the output stream
                if not line:
                    break

                # Try to decode the line as JSON
                # If successful assume the line is from stdout
                try:
                    data = json.loads(line)

                # If the JSON decoding fails
                # Assume the line is from stderr
                except json.JSONDecodeError:

                    # Add the length of the line to the buffer length
                    buffer_length += len(line)

                    # Raise an exception if the maximum output buffer length is exceeded
                    if buffer_length > maximum_buffer_length:
                        raise BufferError("Maximum buffer length exceeded")

                    # Else add the line to the output buffer
                    buffer.append(line)

                    # Continue with the next line
                    continue

                # Raise an exception if the search result was already sent but more data was received
                if self._received_result:
                    raise RuntimeError("Already received a search result")

                # Match the data type
                match data["type"]:

                    # Raise an exception if the search initialization failed
                    case "initialization":
                        if (
                            int(data["start_index"]) != self._start_index
                            or
                            int(data["end_index"]) != self._end_index
                        ):
                            raise RuntimeError("Search initialization failed")

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
                            self._received_result = True

            # Wait until the search process finishes
            self._process.wait()

            # Only do this if the stop event has not been set
            if not self._stop_event.is_set():

                # Raise an exception if the exit code it non zero
                if self._process.returncode != 0:
                    raise RuntimeError(f"Exit code {self._process.returncode}: {''.join(buffer)}")

                # Raise an exception if the search result was never received
                if not self._received_result:
                    raise RuntimeError("Received no search result")

                # Raise and exception if the number of received and found solutions don't match
                if len(self._solutions) != self._solutions_found:
                    raise ValueError("Number of received and found solutions don't match")

                # Set the finished flag
                with self._lock:
                    self._finished = True

        # Catch any unhandled exceptions
        except:

            # Kill the search process
            if self._process != None:
                self._process.kill()

            # Re-raise the exception
            raise

        # Always set the stop event
        finally:
            self._stop_event.set()

    # =============================================================================================
    # Wait for a specified amount of time or until the search is stopped
    # =============================================================================================
    def wait(self, timeout_seconds: float | None = None):
        self._stop_event.wait(timeout = timeout_seconds)

    # =============================================================================================
    # Stop the search thread
    # =============================================================================================
    def stop(self):

        # Set the stop event
        self._stop_event.set()

        # Kill the search process
        if self._process != None:
            self._process.kill()