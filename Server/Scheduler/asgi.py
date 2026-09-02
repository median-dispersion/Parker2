from collections.abc import Coroutine
from http import HTTPStatus

# ASGI class
class ASGI:

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
    # Main ASGI callable
    # =============================================================================================
    async def __call__(self, scope: dict, receive: Coroutine, send: Coroutine):

        # Raise an exception if the ASGI protocol is not HTTP
        if scope["type"] != "http":
            raise NotImplementedError("ASGI protocol not supported!")

        # Handle the HTTP request
        try:

            # Respond with 200 OK
            await self._send_status(send, HTTPStatus.OK)

        # If an unhandled exception occurs
        except Exception:

            # Respond with 500 Internal Server Error
            await self._send_status(send, HTTPStatus.INTERNAL_SERVER_ERROR)

            # Re-raise the exception
            raise

# Initialize the singleton ASGI instance
asgi = ASGI()