from http import HTTPStatus, HTTPMethod
from copy import deepcopy
from typing import Any
import json
from collections.abc import Callable
from codecs import lookup as codecs_lookup
from validation import ValidationError
from urllib.parse import parse_qs
from traceback import format_exc
from sys import exc_info

# =================================================================================================
# Base response class
# =================================================================================================
class Response:

    # =============================================================================================
    # Initialization
    # =============================================================================================
    def __init__(
        self,
        status: HTTPStatus,
        headers: dict[str, str] | None = None,
        body: bytes = b""
    ):

        # Initialize member variables
        self._status = status
        self._headers = headers.copy() if headers != None else {}
        self._body = body

    # =============================================================================================
    # Get the status
    # =============================================================================================
    @property
    def status(self) -> HTTPStatus:
        return self._status

    # =============================================================================================
    # Get the status as a string
    # =============================================================================================
    @property
    def status_string(self) -> str:
        return f"{self._status.value} {self._status.phrase}"

    # =============================================================================================
    # Get the headers
    # =============================================================================================
    @property
    def headers(self) -> dict[str, str]:
        return self._headers.copy()

    # =============================================================================================
    # Get the headers as a list
    # =============================================================================================
    @property
    def headers_list(self) -> list[tuple[str, str]]:
        return [header for header in self._headers.items()]

    # =============================================================================================
    # Get the body
    # =============================================================================================
    @property
    def body(self) -> bytes:
        return self._body

    # =============================================================================================
    # Get the body as a list
    # =============================================================================================
    @property
    def body_list(self) -> list[bytes]:
        return [self._body]

# =================================================================================================
# Text response class
# =================================================================================================
class TextResponse(Response):

    # =============================================================================================
    # Initialization
    # =============================================================================================
    def __init__(
        self,
        status: HTTPStatus,
        headers: dict[str, str] | None = None,
        body: str = "",
        encoding: str = "iso_8859_1"
    ):

        # Initialize member variables
        self._body_string = body
        self._encoding = encoding

        # Copy or initialize the headers
        headers = headers.copy() if headers != None else {}

        # Define the content type header
        content_type_name = "Content-Type"
        content_type_value = f"text/plain; charset={self._encoding}"

        # If the content type header is set, check if its value is correct, else raise an exception
        if content_type_name in headers:
            if content_type_value != headers[content_type_name]:
                raise ValueError("Incorrect content type")

        # If the content type header is not set, set it
        else:
            headers[content_type_name] = content_type_value

        # Call the parent constructor
        super().__init__(
            status = status,
            headers = headers,
            body = self._body_string.encode(self._encoding)
        )

    # =============================================================================================
    # Get the body as a string
    # =============================================================================================
    @property
    def body_string(self) -> str:
        return self._body_string

    # =============================================================================================
    # Get the body encoding
    # =============================================================================================
    @property
    def encoding(self) -> str:
        return self._encoding

# =================================================================================================
# Status response class
# =================================================================================================
class StatusResponse(TextResponse):

    # =============================================================================================
    # Initialization
    # =============================================================================================
    def __init__(
        self,
        status: HTTPStatus,
        headers: dict[str, str] | None = None,
        encoding: str = "iso_8859_1"
    ):
        super().__init__(
            status = status,
            headers = headers,
            body = status.phrase,
            encoding = encoding
        )

# =================================================================================================
# JSON response class
# =================================================================================================
class JSONResponse(Response):

    # =============================================================================================
    # Initialization
    # =============================================================================================
    def __init__(
        self,
        status: HTTPStatus,
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
        encoding: str = "utf-8"
    ):

        # Initialize member variables
        self._body_dict = deepcopy(body) if body != None else {}
        self._encoding = encoding

        # Copy or initialize the headers
        headers = headers.copy() if headers != None else {}

        # Define the content type header
        content_type_name = "Content-Type"
        content_type_value = f"application/json; charset={self._encoding}"

        # If the content type header is set, check if its value is correct, else raise an exception
        if content_type_name in headers:
            if content_type_value != headers[content_type_name]:
                raise ValueError("Incorrect content type")

        # If the content type header is not set, set it
        else:
            headers[content_type_name] = content_type_value

        # Call the parent constructor
        super().__init__(
            status = status,
            headers = headers,
            body = json.dumps(
                obj = self._body_dict,
                default = lambda object: str(object)
            ).encode(self._encoding)
        )

    # =============================================================================================
    # Get the body as a dict
    # =============================================================================================
    @property
    def body_dict(self) -> dict[str, Any]:
        return deepcopy(self._body_dict)

    # =============================================================================================
    # Get the JSON encoding
    # =============================================================================================
    @property
    def encoding(self) -> str:
        return self._encoding

# =================================================================================================
# Base request class
# =================================================================================================
class Request:

    # =============================================================================================
    # Initialization
    # =============================================================================================
    def __init__(
        self,
        method: HTTPMethod,
        path: str,
        query: dict[str, list[str]],
        headers: dict[str, str],
        body: bytes
    ):

        # Initialize member variables
        self._method = method
        self._path = path
        self._query = deepcopy(query)
        self._headers = headers.copy()
        self._body = body

    # =============================================================================================
    # Get the method
    # =============================================================================================
    @property
    def method(self) -> HTTPMethod:
        return self._method

    # =============================================================================================
    # Get the path
    # =============================================================================================
    @property
    def path(self) -> str:
        return self._path

    # =============================================================================================
    # Get the query
    # =============================================================================================
    @property
    def query(self) -> dict[str, list[str]]:
        return deepcopy(self._query)

    # =============================================================================================
    # Get the headers
    # =============================================================================================
    @property
    def headers(self) -> dict[str, str]:
        return self._headers.copy()

    # =============================================================================================
    # Get the body
    # =============================================================================================
    @property
    def body(self) -> bytes:
        return self._body

# =================================================================================================
# JSON request class
# =================================================================================================
class JSONRequest(Request):

    # =============================================================================================
    # Initialization
    # =============================================================================================
    def __init__(
        self,
        method: HTTPMethod,
        path: str,
        query: dict[str, list[str]],
        headers: dict[str, str],
        body: dict[str, Any],
        encoding: str = "utf-8"
    ):

        # Initialize member variables
        self._body_dict = deepcopy(body)
        self._encoding = encoding

        # Raise an exception if the content type is not correct
        if headers["Content-Type"] != f"application/json; charset={self._encoding}":
            raise ValueError("Incorrect content type")

        # Call the parent constructor
        super().__init__(
            method = method,
            path = path,
            query = query,
            headers = headers,
            body = json.dumps(
                obj = self._body_dict,
                default = lambda object: str(object)
            ).encode(self._encoding)
        )

    # =============================================================================================
    # Get the body as a dict
    # =============================================================================================
    @property
    def body_dict(self) -> dict[str, Any]:
        return deepcopy(self._body_dict)

    # =============================================================================================
    # Get the JSON encoding
    # =============================================================================================
    @property
    def encoding(self) -> str:
        return self._encoding

# =================================================================================================
# WSGI class
# =================================================================================================
class WSGI:

    # Type aliases
    type _RequestHandler = Callable[[Request], Response | None]
    type _RequestHandlerDecorator = Callable[[WSGI._RequestHandler], None]

    # =============================================================================================
    # Initialization
    # =============================================================================================
    def __init__(self):

        # Initialize member variables
        self._paths: dict[str, dict[HTTPMethod, WSGI._RequestHandler]] = {}

    # =============================================================================================
    # Add a request handler
    # =============================================================================================
    def _add_handler(self, path: str, method: HTTPMethod, handler: WSGI._RequestHandler):

        # Add the path and return the methods for the path
        methods = self._paths.setdefault(path, {})

        # Raise an exception if the request method is already defined for the path
        if method in methods:
            raise ValueError("Method already defined")

        # Set the request handler
        methods[method] = handler

    # =============================================================================================
    # Add a CONNECT request handler
    # =============================================================================================
    def CONNECT(self, path: str) -> WSGI._RequestHandlerDecorator:

        # Define a decorator that adds the request handler for the given path and method
        def decorator(handler: WSGI._RequestHandler):
            self._add_handler(path, HTTPMethod.CONNECT, handler)

        # Return the decorator
        return decorator

    # =============================================================================================
    # Add a DELETE request handler
    # =============================================================================================
    def DELETE(self, path: str) -> WSGI._RequestHandlerDecorator:

        # Define a decorator that adds the request handler for the given path and method
        def decorator(handler: WSGI._RequestHandler):
            self._add_handler(path, HTTPMethod.DELETE, handler)

        # Return the decorator
        return decorator

    # =============================================================================================
    # Add a GET request handler
    # =============================================================================================
    def GET(self, path: str) -> WSGI._RequestHandlerDecorator:

        # Define a decorator that adds the request handler for the given path and method
        def decorator(handler: WSGI._RequestHandler):
            self._add_handler(path, HTTPMethod.GET, handler)

        # Return the decorator
        return decorator

    # =============================================================================================
    # Add a HEAD request handler
    # =============================================================================================
    def HEAD(self, path: str) -> WSGI._RequestHandlerDecorator:

        # Define a decorator that adds the request handler for the given path and method
        def decorator(handler: WSGI._RequestHandler):
            self._add_handler(path, HTTPMethod.HEAD, handler)

        # Return the decorator
        return decorator

    # =============================================================================================
    # Add a OPTIONS request handler
    # =============================================================================================
    def OPTIONS(self, path: str) -> WSGI._RequestHandlerDecorator:

        # Define a decorator that adds the request handler for the given path and method
        def decorator(handler: WSGI._RequestHandler):
            self._add_handler(path, HTTPMethod.OPTIONS, handler)

        # Return the decorator
        return decorator

    # =============================================================================================
    # Add a PATCH request handler
    # =============================================================================================
    def PATCH(self, path: str) -> WSGI._RequestHandlerDecorator:

        # Define a decorator that adds the request handler for the given path and method
        def decorator(handler: WSGI._RequestHandler):
            self._add_handler(path, HTTPMethod.PATCH, handler)

        # Return the decorator
        return decorator

    # =============================================================================================
    # Add a POST request handler
    # =============================================================================================
    def POST(self, path: str) -> WSGI._RequestHandlerDecorator:

        # Define a decorator that adds the request handler for the given path and method
        def decorator(handler: WSGI._RequestHandler):
            self._add_handler(path, HTTPMethod.POST, handler)

        # Return the decorator
        return decorator

    # =============================================================================================
    # Add a PUT request handler
    # =============================================================================================
    def PUT(self, path: str) -> WSGI._RequestHandlerDecorator:

        # Define a decorator that adds the request handler for the given path and method
        def decorator(handler: WSGI._RequestHandler):
            self._add_handler(path, HTTPMethod.PUT, handler)

        # Return the decorator
        return decorator

    # =============================================================================================
    # Add a TRACE request handler
    # =============================================================================================
    def TRACE(self, path: str) -> WSGI._RequestHandlerDecorator:

        # Define a decorator that adds the request handler for the given path and method
        def decorator(handler: WSGI._RequestHandler):
            self._add_handler(path, HTTPMethod.TRACE, handler)

        # Return the decorator
        return decorator

    # =============================================================================================
    # Only allow requests that contain JSON content
    # =============================================================================================
    @staticmethod
    def requires_json(arguments: dict[str, Callable[[Any], Any]] | None = None) -> WSGI._RequestHandlerDecorator:

        # Define a decorator that returns a wrapper around the request handler
        def decorator(handler: WSGI._RequestHandler) -> WSGI._RequestHandler:

            # Define a wrapper function around the handler function
            def wrapper(request: Request) -> TextResponse | Response | None:

                # Get the request header
                headers = request.headers

                # Get the content type
                content_type = headers.get("Content-Type")

                # If no content type header was found respond with 400 Bad Request
                if not content_type:
                    return TextResponse(status = HTTPStatus.BAD_REQUEST, body = "Missing content type")

                # Split the content type header into its values
                content_type_values = content_type.split(";", maxsplit = 1)

                # Get the actual content type
                content_type = content_type_values[0].strip()

                # If the content type is not "application/json" respond with 400 Bad Request
                if content_type != "application/json":
                    return TextResponse(status = HTTPStatus.BAD_REQUEST, body = "Incorrect content type")

                # Set the character encoding to a default value of "utf-8"
                encoding = "utf-8"

                # If the content type header included a second value extract the character encoding
                if len(content_type_values) == 2:
                    encoding = content_type_values[1].strip().removeprefix("charset=")

                # Try to lookup the character encoding
                try:
                    codecs_lookup(encoding)

                # If the character encoding was not found respond with 400 Bad Request
                except LookupError:
                    return TextResponse(status = HTTPStatus.BAD_REQUEST, body = "Unknown character encoding")

                # Update the headers to match this exact content type value
                headers["Content-Type"] = f"application/json; charset={encoding}"

                # Get the request body
                body = request.body

                # If the body is missing respond with 400 Bad Request
                if not body:
                    return TextResponse(status = HTTPStatus.BAD_REQUEST, body = "Missing body")

                # Try to decode the body
                try:
                    body = request.body.decode(encoding)

                # If the body can't be decoded
                except UnicodeDecodeError:
                    return TextResponse(status = HTTPStatus.BAD_REQUEST, body = "Body not decodable")

                # Try to parse the body as JSON
                try:
                    body = json.loads(body)

                # If the body can't be parsed as JSON
                except json.JSONDecodeError:
                    return TextResponse(status = HTTPStatus.BAD_REQUEST, body = "Invalid JSON body")

                # Loop through all required JSON arguments
                if arguments:
                    for argument, validate in arguments.items():

                        # If the argument is missing respond with 400 Bad Request
                        if argument not in body:
                            return TextResponse(status = HTTPStatus.BAD_REQUEST, body = "Missing argument")

                        # Try to validate the argument
                        try:
                            value = validate(body[argument])

                            # Update the body if an updated value was returned by the validation
                            if value:
                                body[argument] = value

                        # If the argument validation failed respond with 400 Bad Request
                        except ValidationError as reason:
                            return TextResponse(status = HTTPStatus.BAD_REQUEST, body = str(reason))

                # Call the handler function
                return handler(JSONRequest(
                    method = request.method,
                    path = request.path,
                    query = request.query,
                    headers = headers,
                    body = body,
                    encoding = encoding
                ))

            # Return the wrapper function
            return wrapper

        # Return the decorator
        return decorator

    # =============================================================================================
    # Send a response
    # =============================================================================================
    @staticmethod
    def _respond(
        start_response: Callable,
        response: Response,
        exception_info: tuple | None = None
    ) -> list[bytes]:

        # Start the response
        start_response(response.status_string, response.headers_list, exception_info)

        # Return the body as list
        return response.body_list

    # =============================================================================================
    # Get the request headers
    # =============================================================================================
    @staticmethod
    def _get_headers(environment: dict[str, Any]) -> dict[str, str]:

        # Request headers
        headers = {}

        # Set the content type header
        if "CONTENT_TYPE" in environment:
            headers["Content-Type"] = environment["CONTENT_TYPE"]

        # Set the content length header
        if "CONTENT_LENGTH" in environment:
            headers["Content-Length"] = environment["CONTENT_LENGTH"]

        # Loop through all WSGI environment variables
        for name, value in environment.items():

            # Check if the variable is a header by checking if it starts with HTTP_
            if name.startswith("HTTP_"):

                # Normalize the header name
                name = "-".join([segment.lower().capitalize() for segment in name.removeprefix("HTTP_").split("_")])

                # Add the header
                headers[name] = value

        # Return all request headers
        return headers

    # =============================================================================================
    # Main WSGI callable
    # =============================================================================================
    def __call__(self, environment: dict[str, Any], start_response: Callable) -> list[bytes]:

        # Handle HTTP requests
        try:

            # Try to get the request path
            path = environment.get("PATH_INFO", "")

            # Try to get the methods for the request path
            methods = self._paths.get(path)

            # If no methods where found respond with 404 Not Found
            if not methods:
                return WSGI._respond(start_response, StatusResponse(HTTPStatus.NOT_FOUND))

            # Try to get the request method
            method = environment.get("REQUEST_METHOD", "")

            # Try to get the handler function for the request method
            handler = methods.get(method)

            # If no handler function was found respond with 405 Method Not Allowed
            if not handler:
                return WSGI._respond(start_response, StatusResponse(HTTPStatus.METHOD_NOT_ALLOWED))

            # Call the handler function
            response = handler(Request(
                method = HTTPMethod(method),
                path = path,
                query = parse_qs(environment.get("QUERY_STRING", "")),
                headers = WSGI._get_headers(environment),
                body = environment["wsgi.input"].read()
            ))

            # If the handler didn't return a response, respond with 200 OK
            if not response:
                return WSGI._respond(start_response, StatusResponse(HTTPStatus.OK))

            # Send the response
            return WSGI._respond(start_response, response)

        # If an unhandled exception occurs
        except:

            # Write the formatted exception to the WSGI error stream
            environment["wsgi.errors"].write(format_exc())

            # Respond with 500 internal server error
            return WSGI._respond(
                start_response,
                StatusResponse(HTTPStatus.INTERNAL_SERVER_ERROR),
                exc_info()
            )