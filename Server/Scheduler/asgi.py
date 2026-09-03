from collections.abc import Callable, Coroutine
from http import HTTPStatus
import json
from urllib.parse import parse_qs

# ASGI class
class ASGI:

    # =============================================================================================
    # Initialization
    # =============================================================================================
    def __init__(self):
        self._paths = {}

    # =============================================================================================
    # Add a GET path
    # =============================================================================================
    def GET(self, path: str) -> Callable:

        # Define a decorator that sets a handler function for the given path and method
        def decorator(handler: Coroutine):
            self._paths.setdefault(path, {})["GET"] = handler

        # Return the decorator
        return decorator

    # =============================================================================================
    # Add a POST path
    # =============================================================================================
    def POST(self, path: str) -> Callable:

        # Define a decorator that sets a handler function for the given path and method
        def decorator(handler: Coroutine):
            self._paths.setdefault(path, {})["POST"] = handler

        # Return the decorator
        return decorator

    # =============================================================================================
    # Only allow request that contain a JSON body
    # =============================================================================================
    def requires_json_body(self, handler: Coroutine) -> Coroutine:

        # Define a wrapper function around the handler
        async def wrapper(request: dict) -> dict | None:

            # Bad request response data
            status = HTTPStatus.BAD_REQUEST
            bad_request = {
                "status": status.value,
                "body": status.phrase
            }

            # Get the request headers
            headers = request.get("headers")

            # If there are no request headers respond with 400 Bad Request
            if not headers:
                return bad_request

            # Get the content type
            content_type = headers.get("content-type")

            # If there is no content type or the content type is not JSON respond with 400 Bad Request
            if not content_type or content_type[0] != "application/json":
                return bad_request

            # Get the request body
            body = request.get("body")

            # If the request contains no body respond with 400 Bad Request
            if not body:
                return bad_request

            # Try to parse the request body as JSON
            try:
                request["body"] = json.loads(body)

            # If the body can not be parsed as JSON respond with 400 Bad Request
            except json.JSONDecodeError:
                return bad_request

            # Call the handler function with the parsed body
            return await handler(request)

        # Return the wrapper function
        return wrapper

    # =============================================================================================
    # Send a basic HTTP status response
    # =============================================================================================
    async def _send_status(self, send: Coroutine, status: HTTPStatus):

        # Send response start
        await send({
            "type": "http.response.start",
            "status": status.value
        })

        # Send response body
        await send({
            "type": "http.response.body",
            "body": status.phrase.encode("utf-8")
        })

    # =============================================================================================
    # Get the request headers
    # =============================================================================================
    def _get_headers(self, header_list: list) -> dict | None:

        # Dictionary of all header
        headers = {}

        # Loop through all headers in the request
        for name, value in header_list:

            # Add the decoded header
            headers.setdefault(name.decode("utf-8").lower(), []).append(value.decode("utf-8"))

        # If there are no headers return None
        if not headers:
            return None

        # Return all headers
        return headers

    # =============================================================================================
    # Get the request query
    # =============================================================================================
    def _get_query(self, query_bytes: bytes) -> dict | None:

        # Parse the query string
        query = parse_qs(query_bytes.decode("utf-8"))

        # If there are no query arguments return None
        if not query:
            return None

        # Return the request query
        return query

    # =============================================================================================
    # Get the request body
    # =============================================================================================
    async def _get_body(self, receive: Coroutine) -> str | None:

        # Raw request body
        body = b""

        # Loop until no more data is available
        while True:

            # Receive the event
            event = await receive()

            # Raise an exception if the event type is not http.request
            if event["type"] != "http.request":
                raise NotImplementedError("Event type not supported!")

            # Add the received request body
            body += event.get("body", b"")

            # Break the loop if no more body data is available
            if not event.get("more_body", False):
                break

        # Return None if the body is empty
        if body == b"":
            return None

        # Return the decoded body
        return body.decode("utf-8")

    # =============================================================================================
    # Construct response
    # =============================================================================================
    async def _send_response(self, send: Coroutine, data: dict):

        # Initialize the response start
        response_start = {
            "type": "http.response.start",
            "status": data["status"]
        }

        # If the data contains response headers
        if "headers" in data and data["headers"]:

            # Add headers to the response start
            headers = response_start.setdefault("headers", [])

            # Encode each header and add it to the response start
            for name, value in data["headers"].items():
                headers.append((
                    name.encode("utf-8"),
                    value.encode("utf-8")
                ))

        # Initialize the response body
        response_body = {"type": "http.response.body"}

        # If the data contains a body encode it and add it to the response body
        if "body" in data and data["body"]:
            response_body["body"] = data["body"].encode("utf-8")

        # Send the response
        await send(response_start)
        await send(response_body)

    # =============================================================================================
    # Main ASGI callable
    # =============================================================================================
    async def __call__(self, scope: dict, receive: Coroutine, send: Coroutine):

        # Raise an exception if the ASGI protocol is not HTTP
        if scope["type"] != "http":
            raise NotImplementedError("ASGI protocol not supported!")

        # Handle the HTTP request
        try:

            # Get all methods for the request path
            methods = self._paths.get(scope["path"])

            # If no methods where found respond with 404 Not Found
            if not methods:
                await self._send_status(send, HTTPStatus.NOT_FOUND)
                return

            # Get the handler function for the request method
            handler = methods.get(scope["method"])

            # If no handler is set for the request method respond with 405 Method Not Allowed
            if not handler:
                await self._send_status(send, HTTPStatus.METHOD_NOT_ALLOWED)
                return

            # Get the request headers
            headers = self._get_headers(scope["headers"])

            # Get the request query
            query = self._get_query(scope["query_string"])

            # Get the request body
            body = await self._get_body(receive)

            # Call the handler function
            data = await handler({
                "headers": headers,
                "query": query,
                "body": body
            })

            # If no data was returned respond with 200 OK
            if not data:
                await self._send_status(send, HTTPStatus.OK)
                return

            # Send a response
            await self._send_response(send, data)

        # If an unhandled exception occurs
        except:

            # Respond with 500 Internal Server Error
            await self._send_status(send, HTTPStatus.INTERNAL_SERVER_ERROR)

            # Re-raise the exception
            raise

# Initialize the singleton ASGI instance
asgi = ASGI()