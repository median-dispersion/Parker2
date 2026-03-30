import os
from settings import settings
import signal
from client import Client

# List of all client threads
clients = []

# =================================================================================================
# Get the number of available CPU cores
# =================================================================================================
def get_available_cpu_cores() -> int:

    # Get the total number of CPU cores
    available_cpu_cores = os.cpu_count()

    # If no core count was provided return at 1 available CPU core
    if available_cpu_cores is None:
        return 1

    # Subtract the number of idle CPU cores from the total
    available_cpu_cores -= settings.client_idle_cpu_cores

    # Return the number of available CPU cores with a minimum of at least 1 core
    return max(available_cpu_cores, 1)

# =================================================================================================
# Stop the client threads
# =================================================================================================
def stop_clients(signum, frame) -> None:

    global clients

    # Loop through the list of clients
    for client in clients:

        # Stop each client
        client.stop()

        # Print a status message
        print(f"{client.name}: Stopped")

# =================================================================================================
# Main function
# =================================================================================================
def main() -> None:

    # Get the number of available CPU cores
    available_cpu_cores = get_available_cpu_cores()

    # Register signal handlers to stop the client threads in the event of in interrupt or termination
    signal.signal(signal.SIGINT, stop_clients)
    signal.signal(signal.SIGTERM, stop_clients)

    global clients

    # Start a client thread for each available CPU core
    for client_index in range(available_cpu_cores):

        # Initialize the client thread
        client = Client(f"{settings.client_name}-{client_index}")

        # Start the client thread
        client.start()

        # Print a status message
        print(f"{client.name}: Started")

        # Add the client thread to the list of all client threads
        clients.append(client)

# Check if running directly instead of being imported as a module
if __name__ == "__main__":

    # Run the main function
    main()