from collections import defaultdict
from collections.abc import Callable, Iterable
from http import HTTPStatus
import json
from urllib.parse import parse_qs
from typing import IO
import traceback

# WSGI class
class WSGI:

    # =============================================================================================
    # Initialization
    # =============================================================================================
    def __init__(self):
        self._paths = defaultdict(dict)

    # =============================================================================================
    # Add a GET path
    # =============================================================================================
    def GET(self, path: str) -> Callable:

        # Define a decorator that sets a handler function for the given path and method
        def decorator(handler: Callable):
            self._paths[path]["GET"] = handler

        # Return the decorator
        return decorator

    # =============================================================================================
    # Add a POST path
    # =============================================================================================
    def POST(self, path: str) -> Callable:

        # Define a decorator that sets a handler function for the given path and method
        def decorator(handler: Callable):
            self._paths[path]["POST"] = handler

        # Return the decorator
        return decorator

    # =============================================================================================
    # Only allow request that contain a JSON body
    # =============================================================================================
    def requires_json_body(self, handler: Callable) -> Callable:

        # Define a wrapper function around the handler
        def wrapper(request: dict) -> dict | None:

            # Get the request headers
            headers = request.get("headers")

            # If there are no request headers respond with 400 Bad Request
            if not headers:
                return {
                    "status": HTTPStatus.BAD_REQUEST,
                    "body": "Missing headers!"
                }

            # Get the content type
            content_type = headers.get("content_type")

            # If there is no content type respond with 400 Bad Request
            if not content_type:
                return {
                    "status": HTTPStatus.BAD_REQUEST,
                    "body": "Missing content type!"
                }

            # If the content type is not "application/json" respond with 400 Bad Request
            if content_type != "application/json":
                return {
                    "status": HTTPStatus.BAD_REQUEST,
                    "body": "Incorrect content type!"
                }

            # Get the request body
            body = request.get("body")

            # If the request contains no body respond with 400 Bad Request
            if not body:
                return {
                    "status": HTTPStatus.BAD_REQUEST,
                    "body": "Missing body!"
                }

            # Try to parse the request body as JSON
            try:
                request["body"] = json.loads(body)

            # If the body can not be parsed as JSON respond with 400 Bad Request
            except json.JSONDecodeError:
                return {
                    "status": HTTPStatus.BAD_REQUEST,
                    "body": "Body not parsable!"
                }

            # Call the handler function with the parsed body
            return handler(request)

        # Return the wrapper function
        return wrapper

    # =============================================================================================
    # Send a response
    # =============================================================================================
    def _send_response(self, start_response: Callable, response: dict) -> Iterable:

        # Construct the status string
        status_string = f"{response['status'].value} {response['status'].phrase}"

        # Response headers
        headers = []

        # Add all headers
        if "headers" in response:
            for name, value in response["headers"].items():
                headers.append((name, value))

        # Start the response
        start_response(status_string, headers)

        # If the response contains a body, encode and return it
        if "body" in response:
            return [response["body"].encode("utf-8")]

        # Return an empty response body
        return []

    # =============================================================================================
    # Construct a basic response from an HTTP status
    # =============================================================================================
    def _status_response(self, status: HTTPStatus) -> dict:
        return {
            "status": status,
            "body": status.phrase
        }

    # =============================================================================================
    # Get the request headers
    # =============================================================================================
    def _get_headers(self, environment: dict) -> dict | None:

        # HTTP headers
        headers = {}

        # If content type is set add it to the request headers
        if "CONTENT_TYPE" in environment:
            headers["content_type"] = environment["CONTENT_TYPE"]

        # If content length is set add it to the request headers
        if "CONTENT_LENGTH" in environment:
            headers["content_length"] = environment["CONTENT_LENGTH"]

        # Get all HTTP headers from the WSGI environment
        for name, value in environment.items():
            if name.startswith("HTTP_"):
                headers[name.removeprefix("HTTP_").lower()] = value

        # If there are no request headers return None
        if not headers:
            return None

        # Return the HTTP headers
        return headers

    # =============================================================================================
    # Get the request query
    # =============================================================================================
    def _get_query(self, query_string: str) -> dict | None:

        # Parse the query string
        query = parse_qs(query_string)

        # If there are no query arguments return None
        if not query:
            return None

        # Return the request query
        return query

    # =============================================================================================
    # Get the request body
    # =============================================================================================
    def _get_body(self, input: IO) -> str | None:

        # Read and decode the request body
        body = input.read().decode("utf-8")

        # If the request contains no body return None
        if not body:
            return None

        # Return the request body
        return body

    # =============================================================================================
    # Main WSGI callable
    # =============================================================================================
    def __call__(self, environment: dict, start_response: Callable) -> Iterable:

        # Handle the HTTP request
        try:

            # Get all methods for the request path
            methods = self._paths.get(environment.get("PATH_INFO", ""))

            # If no methods where found respond with 404 Not Found
            if not methods:
                return self._send_response(start_response, self._status_response(HTTPStatus.NOT_FOUND))

            # Get the handler function for the request method
            handler = methods.get(environment.get("REQUEST_METHOD", ""))

            # If no handler is set for the request method respond with 405 Method Not Allowed
            if not handler:
                return self._send_response(start_response, self._status_response(HTTPStatus.METHOD_NOT_ALLOWED))

            # Get the request headers
            headers = self._get_headers(environment)

            # Get the request query
            query = self._get_query(environment.get("QUERY_STRING", ""))

            # Get the request body
            body = self._get_body(environment["wsgi.input"])

            # Call the handler function
            response = handler({
                "headers": headers,
                "query": query,
                "body": body
            })

            # If no response was returned respond with a generic 200 OK
            if not response:
                return self._send_response(start_response, self._status_response(HTTPStatus.OK))

            # Send the response
            return self._send_response(start_response, response)

        # If an unhandled exception occurs
        except Exception:

            # Print the exception
            environment["wsgi.errors"].write(traceback.format_exc())

            # Respond with 500 Internal Server Error
            return self._send_response(start_response, self._status_response(HTTPStatus.INTERNAL_SERVER_ERROR))

# Initialize the singleton WSGI instance
wsgi = WSGI()