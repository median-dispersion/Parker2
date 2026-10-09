import settings
from worker import Worker
import logging
import signal

# List of all worker threads
workers = []

# =================================================================================================
# Start all worker threads
# =================================================================================================
def start():

    # Create worker threads
    for thread_id in range(settings.worker_threads):
        workers.append(Worker(thread_id))

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

    # On termination, stop all worker thread gracefully
    if number in [signal.SIGINT, signal.SIGTERM]:
        stop()

    # Reset the signal handlers for the termination events to the default
    # Pressing Ctrl+C will then force stop all workers
    # On OS shutdown a SIGKILL will force stop all workers that have not stopped in time
    if number == signal.SIGINT:
        signal.signal(signal.SIGINT, signal.SIG_DFL)
    if number == signal.SIGTERM:
        signal.signal(signal.SIGTERM, signal.SIG_DFL)

# Check if the module is called as a script
if __name__ == "__main__":

    # Initialize the logger
    logging.basicConfig(level=logging.INFO)

    # Register signal handlers for worker termination
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start all worker threads
    start()