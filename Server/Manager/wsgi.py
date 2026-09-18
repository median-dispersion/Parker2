from http import HTTPStatus
from collections.abc import Callable
from traceback import format_exc

# =================================================================================================
# Response class
# =================================================================================================
class Response:

    # =============================================================================================
    # Initialization
    # =============================================================================================
    def __init__(self, status: HTTPStatus, headers: dict = {}, body: str = ""):

        self._status = status
        self._headers = headers
        self._body = body

    # =============================================================================================
    # Get the status
    # =============================================================================================
    def get_status(self, style: type = HTTPStatus) -> HTTPStatus | str:

        # Return the status as a HTTPStatus
        if style == HTTPStatus:
            return self._status

        # Return the status as a string
        if style == str:
            return f"{self._status.value} {self._status.phrase}"

        # Raise an exception if the style is not supported
        raise TypeError("Unsupported style")

    # =============================================================================================
    # Get the headers
    # =============================================================================================
    def get_headers(self, style: type = dict) -> dict | list:

        # Return the headers as a dict
        if style == dict:
            return self._headers

        # Return the headers as a list
        if style == list:
            return [(name, value) for name, value in self._headers.items()]

        # Raise an exception if the style is not supported
        raise TypeError("Unsupported style")

    # =============================================================================================
    # Get the body
    # =============================================================================================
    def get_body(self, style: type = str, encoding: str = "utf-8") -> str | bytes:

        # Return the body as a string
        if style == str:
            return self._body

        # Return the body as bytes
        if style == bytes:
            return self._body.encode(encoding)

        # Raise an exception if the style is not supported
        raise TypeError("Unsupported style")

# =================================================================================================
# WSGI class
# =================================================================================================
class WSGI:

    # =============================================================================================
    # Send a response to the client
    # =============================================================================================
    def _respond(self, start_response: Callable, response: Response) -> list:

        # Start the response
        start_response(response.get_status(str), response.get_headers(list))

        # Return the encoded body iterable
        return [response.get_body(bytes)]

    # =============================================================================================
    # Main WSGI callable
    # =============================================================================================
    def __call__(self, environment: dict, start_response: Callable) -> list:

        # Handle HTTP requests
        try:

            # Respond with a 200 OK
            return self._respond(start_response, Response(status = HTTPStatus.OK, body = HTTPStatus.OK.phrase))

        # If an unhandled exception occurs
        except:

            # Print the exception
            environment["wsgi.errors"].write(format_exc())

            # Respond with a 500 Internal Server Error
            return self._respond(start_response, Response(status = HTTPStatus.INTERNAL_SERVER_ERROR, body = HTTPStatus.INTERNAL_SERVER_ERROR.phrase))