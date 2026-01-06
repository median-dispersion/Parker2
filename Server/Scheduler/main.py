import asyncio
import signal
import subprocess
from settings import settings

# Server process
server = None

# =================================================================================================
# Stop the server process
# =================================================================================================
def stop_server(signum, frame):

    global server

    # Check if the server is initialized
    if server is not None:

        # Stop the server process
        server.terminate()

# =================================================================================================
# Main function
# =================================================================================================
async def main():

    global server

    # Register signal handlers to stop the server process in the event of in interrupt or termination
    signal.signal(signal.SIGINT, stop_server)
    signal.signal(signal.SIGTERM, stop_server)

    # Start the server process
    server = subprocess.Popen([
        "fastapi", "run",
        "--host", str(settings.fastapi_host),
        "--port", str(settings.fastapi_port),
        "--workers", str(settings.fastapi_workers),
        "api.py"
    ])

    # Wait for the server process to stop
    server.wait()

# Check if running directly instead of being imported as a module
if __name__ == "__main__":

    # Run the main function
    asyncio.run(main())