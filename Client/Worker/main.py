import logging
import settings
from worker import Worker
import signal

# Get the main logger
logger = logging.getLogger("Main")

# List of all worker threads
workers = []

# =================================================================================================
# Start all worker threads
# =================================================================================================
def start():

    # Log the start event
    logger.info("Starting worker threads...")

    # Create worker threads
    for thread_index in range(settings.worker_threads):
        workers.append(Worker(thread_index))

    # Start all worker threads
    for worker in workers:
        worker.start()

    # Wait for all worker threads to complete
    for worker in workers:
        worker.join()

# =================================================================================================
# Stop all worker threads
# =================================================================================================
def stop():
    for worker in workers:
        worker.stop()

# =================================================================================================
# Signal event handler
# =================================================================================================
def signal_handler(number, frame):

    # If it is a termination signal
    if number in [signal.SIGINT, signal.SIGTERM]:

        # Stop all workers gracefully
        stop()

        # Reset the signal handlers for the termination events to the default
        # Pressing Ctrl+C will then force stop all workers
        # On OS shutdown a SIGKILL will force stop all workers that have not stopped in time
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)

        # Log an info message
        logger.info("Send another termination signal to force stop all workers")

# =================================================================================================
# Main function
# =================================================================================================
def main():

    # Initialize the logger
    logging.basicConfig(level = settings.manager_log_level)

    # Suppress urllib3 debug messages
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    # Register signal handlers for worker termination
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start all worker threads
    start()

# Check if the module is called as a script, then run the main function
if __name__ == "__main__":
    main()