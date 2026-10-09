import requests
import time

# =================================================================================================
# Session class
# =================================================================================================
class Session(requests.Session):

    # =============================================================================================
    # Custom wrapper around the request function
    # =============================================================================================
    def request(
        self,
        *args,
        timeout: float | tuple = 30.0,
        retries: int = 10,
        **kwargs
    ):

        # Raise an exception if there are too few retries
        if retries < 1:
            raise ValueError("Too few retries")

        # Retry the request until successful
        # Or the maximum number of retires has been reached
        for attempt in range(retries):

            # Try to make the request
            try:
                response = super().request(*args, timeout = timeout, **kwargs)

            # If a request connection or timeout error occurs
            except (requests.ConnectionError, requests.Timeout):

                # Re-raise the exception if it was the last retry attempt
                if attempt == retries - 1:
                    raise

                # Else delay the next attempt using exponential backoff to a maximum of 30 seconds
                time.sleep(min(0.5 * (2 ** attempt), 30))

            # If no exceptions occurred
            else:

                # Raise an exception if the response is an error
                response.raise_for_status()

                # Else return the response
                return response