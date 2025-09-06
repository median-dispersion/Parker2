import json
import sys
import queue
import os
import time
from Logger import logger
from Worker import Worker

# =================================================================================================
# Validate data structure
# =================================================================================================
def validateDataStructure(data, structure, path="root"):

    # For every key value pair in the data structure
    for key, value in structure.items():

        # Check if the key is missing in the data then raise an exception
        if key not in data: raise Exception(f"Missing key: '{path}.{key}'!")

        # If the value of the structure is a dict
        if isinstance(value, dict):

            # Check if value in the data is also a dict if not raise an exception
            if not isinstance(data[key], dict): raise Exception(f"Expected 'dict' at '{path}.{key}' got '{type(data[key]).__name__}'!")

            # Recursively validate the dict
            validateDataStructure(data[key], value, f"{path}.{key}")

        # If value type of structure and data don't, match raise an exception
        if not isinstance(data[key], type(value)): raise Exception(f"Expected '{type(value).__name__}' at '{path}.{key}' got '{type(data[key]).__name__}'!")

# =================================================================================================
# Main
# =================================================================================================
if __name__ == "__main__":

    # Configuration structure 
    # This will be loaded from the configuration file!
    configuration = {

        "logger": {

            "filePath": "./client.log",
            "debug":    True,
            "info":     True,
            "success":  True,
            "warning":  True,
            "error":    True

        },

        "server": {

            "host":   "localhost",
            "port":   5000,
            "apiKey": "API-Key",

            "request": {

                "delaySeconds":   1,
                "timeoutSeconds": 30

            }

        },

        "search": {

            "filePath":              "./search.json",
            "binaryPath":            "../Search Binary/search.out",
            "targetDurationSeconds": 300,
            "timeoutFactor":         3,
            "idleCores":             1

        }

    }

    # Try loading the configuration file
    try:

        # Read the configuration file
        with open("./configuration.json", "r") as file: configurationData = json.load(file)

        # Validate configuration data structure
        validateDataStructure(configurationData, configuration, "configuration")

        # Set the configuration to the loaded configuration data
        configuration = configurationData

    # If loading the configuration file fails
    except Exception as exception:

        # Log an error message
        logger.error(f"Failed to load configuration file! Exception: {exception}.")

        # Terminate immediately
        sys.exit(1)

    # Initialize the logger
    if configuration["logger"]["filePath"] != "": logger.setFilePath(configuration["logger"]["filePath"])
    logger.setLevel(logger.Level.DEBUG,   configuration["logger"]["debug"])
    logger.setLevel(logger.Level.INFO,    configuration["logger"]["info"])
    logger.setLevel(logger.Level.SUCCESS, configuration["logger"]["success"])
    logger.setLevel(logger.Level.WARNING, configuration["logger"]["warning"])
    logger.setLevel(logger.Level.ERROR,   configuration["logger"]["error"])

    # Log a info message
    logger.info(f"Initialized logger! Output path: '{configuration["logger"]["filePath"]}', debug: '{configuration["logger"]["debug"]}', info: '{configuration["logger"]["info"]}', success: '{configuration["logger"]["success"]}', warning: '{configuration["logger"]["warning"]}', error: '{configuration["logger"]["error"]}'.")

    # Search structure
    search = {

        "results": []

    }

    # Try loading the search data
    try:

        try:

            # Read the search data
            with open(configuration["search"]["filePath"], "r") as file: searchData = json.load(file)

            # Validate search data structure
            validateDataStructure(searchData, search, "search")

            # Set the search data to the loaded search data
            search = searchData

        # If search data file was not found
        except FileNotFoundError:

            # Create a new search data file
            with open(configuration["search"]["filePath"], "w") as file: json.dump(search, file, indent=4)

            # Log a warning message
            logger.warning(f"Failed to load search data! File '{configuration["search"]["filePath"]}' was not found. Created a new file.")

    # If an exception occurs
    except Exception as exception:

        # Log an error message
        logger.error(f"Failed to load search data! Exception: '{exception}'.")

        # Terminate immediately
        sys.exit(1)

    # Log info message
    logger.info(f"Initialized search data! Loaded results: '{len(search["results"])}'.")

    # Worker report queue
    reportQueue = queue.Queue()

    # List of worker threads
    workers = []

    # Number of worker threads
    threadCount = max(int(os.cpu_count() - configuration["search"]["idleCores"]), 1)

    # Log info message
    logger.info(f"Dispatching '{threadCount}' worker threads...")

    # For each worker thread
    for workerID in range(threadCount):

        # Stagger worker start
        time.sleep(1)

        # Create a new worker
        worker = Worker(

            workerID,
            reportQueue,
            f"{configuration["server"]["host"]}:{configuration["server"]["port"]}",
            configuration["server"]["apiKey"],
            configuration["server"]["request"]["delaySeconds"],
            configuration["server"]["request"]["timeoutSeconds"],
            configuration["search"]["binaryPath"],
            configuration["search"]["targetDurationSeconds"],
            configuration["search"]["timeoutFactor"]

        )

        # Daemon thread
        worker.daemon = True

        # Add the worker to the list of workers
        workers.append(worker)

        # Start the worker
        worker.start()

        # Log info message
        logger.info(f"Dispatched worker '{workerID}'!")

    # Main loop
    try:

        while True:

            # While the worker report queue is not empty
            while not reportQueue.empty():

                    # Get the next report form the queue
                    report = reportQueue.get()

                    # Report message with the correct log level
                    if report["category"] == "status":    logger.info(report["message"])
                    if report["category"] == "exception": logger.error(report["message"])

                    # If the report is a list of results
                    if report["category"] == "results":

                        # Log a success message
                        logger.success(report["message"])

                        # Add the results to the search data
                        search["results"] += report["data"]

                        # Write search data to disk
                        with open(configuration["search"]["filePath"], "w") as file: json.dump(search, file, indent=4)

            # Avoid busy waiting
            time.sleep(0.1)

    # If an exception occurs
    except: 

        pass

    # Finally
    finally:

        # Log info message
        logger.info("Stopping worker threads...")

        # Stop worker threads
        for worker in workers: worker.stop()
        for worker in workers: worker.join()