from http import HTTPStatus, HTTPMethod
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
    def get_body(self, style: type = str, encoding: str = "latin-1") -> str | bytes:

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
    # Initialization
    # =============================================================================================
    def __init__(self):
        self._paths = {}

    # =============================================================================================
    # Add a POST path
    # =============================================================================================
    def POST(self, path: str) -> Callable:

        # Define a decorator function
        def decorator(function: Callable):

            # Add the path
            methods = self._paths.setdefault(path, {})

            # Raise an exception if the request method is already defined
            if HTTPMethod.POST in methods:
                raise ValueError("Method already defined")

            # Set the request method and handler function
            methods[HTTPMethod.POST] = function

        # Return the decorator function
        return decorator

    # =============================================================================================
    # Send a response to the client
    # =============================================================================================
    @staticmethod
    def _respond(start_response: Callable, response: Response) -> list:

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

            # Get all methods for the request path
            methods = self._paths.get(environment.get("PATH_INFO", ""))

            # If no methods where found respond with 404 Not Found
            if not methods:
                return WSGI._respond(
                    start_response,
                    Response(
                        status = HTTPStatus.NOT_FOUND,
                        body = HTTPStatus.NOT_FOUND.phrase
                    )
                )

            # Get the handler function for the request method
            function = methods.get(environment.get("REQUEST_METHOD", ""))

            # If no handler function was found respond with 405 Method Not Allowed
            if not function:
                return WSGI._respond(
                    start_response,
                    Response(
                        status = HTTPStatus.METHOD_NOT_ALLOWED,
                        body = HTTPStatus.METHOD_NOT_ALLOWED.phrase
                    )
                )

            # Respond with 200 OK
            return WSGI._respond(
                start_response,
                Response(
                    status = HTTPStatus.OK,
                    body = HTTPStatus.OK.phrase
                )
            )

        # If an unhandled exception occurs
        except:

            # Print the exception
            environment["wsgi.errors"].write(format_exc())

            # Respond with 500 Internal Server Error
            return WSGI._respond(
                start_response,
                Response(
                    status = HTTPStatus.INTERNAL_SERVER_ERROR,
                    body = HTTPStatus.INTERNAL_SERVER_ERROR.phrase
                )
            )