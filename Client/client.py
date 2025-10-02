from configuration import configuration
from logger import logger
from worker import Worker
import json
import queue
import os
import time

# =================================================================================================
# Main
# =================================================================================================
if __name__ == "__main__":

    # Search data results
    results = []

    # Try reading in the search data results
    try:

        # Load search data results from file
        with open(configuration["search"]["filePath"], "r") as file: results = json.load(file)

    # If the search data results file is not found
    except FileNotFoundError:

        # Log warning message
        logger.warning(f"Failed loading results from '{configuration['search']['filePath']}'! File not found! Creating new file!")

        # Write empty search data results to file
        with open(configuration["search"]["filePath"], "w") as file: json.dump(results, file, indent=4)

    # List of worker threads
    workers = []

    # Output queue
    output = queue.Queue()

    # For every none idle CPU core limited to a minimum of at least 1 core
    for core in range(max(int(os.cpu_count() - configuration["search"]["idleCores"]), 1)):

        # Log info message
        logger.info(f"Starting worker '{core}'...")

        # Create a new worker thread
        worker = Worker(output)

        # Daemon thread
        worker.daemon = True

        # Start the worker thread
        worker.start()

        # Add the worker thread to the list of worker threads
        workers.append(worker)

        # Stagger next worker start
        time.sleep(1)

    # Main loop
    while True:

        # Avoid busy waiting
        time.sleep(1)

        # Loop until the output queue is empty
        while not output.empty():

            # Get the next message from the output queue
            message = output.get()

            # Log the message with the correct log level
            if message["event"] == "info":  logger.info (f"Worker '{message['id']}': {message['data']}")
            if message["event"] == "error": logger.error(f"Worker '{message['id']}': {message['data']}")

            # If the message is a results
            if message["event"] == "results":

                # Log success message
                logger.success(f"Worker '{message['id']}' found a result! Result data: '{message['data']}'.")

                # Add the result
                results.extend(message['data'])

                # Write search data results to file
                with open(configuration["search"]["filePath"], "w") as file: json.dump(results, file, indent=4)