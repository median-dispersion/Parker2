import threading
import json
import sys
import time
from flask import Flask, jsonify, request
from Logger import logger
from Job import Job

server = Flask(__name__)

# =================================================================================================
# Authorize a client request
# =================================================================================================
def authorizeRequest(function):

    # Wrapper function
    def wrapper(*args, **kwargs):

        # Get the authorization header
        authorizationHeader = request.headers.get("Authorization")

        # Check if the authorization header is valid
        if authorizationHeader != None and authorizationHeader.startswith("Bearer "):

            # Get the API key
            apiKey = authorizationHeader.split(" ")[1]

            # Check if the API key matches
            if apiKey == configuration["server"]["apiKey"]:

                # Return
                return function(*args, **kwargs)

        # If the request didn't contain a valid authorization header or API key

        # Log a warning message
        logger.warning(f"Unauthorized request from '{request.remote_addr}' on '{request.path}'! Missing or invalid API key!")

        # Return a 401 - Unauthorized
        return jsonify({"status": 401, "message": "Unauthorized - Missing or invalid API key!"}), 401

    wrapper.__name__ = function.__name__

    # Return the wrapper function
    return wrapper

# =================================================================================================
# Get a new job
# =================================================================================================
@server.route("/job", methods=["GET"])
@authorizeRequest
def getJob():

    # Get the requested range size
    rangeSize = request.args.get("rangeSize", type=int)

    # If no range size was provided
    if rangeSize == None:

        # Log a warning message
        logger.warning(f"Bad request from '{request.remote_addr}' on '{request.path}'! No range size was provided!")

        # Return a 400 - Bad Request
        return jsonify({"status": 400, "message": "Bad Request - No range size was provided!"}), 400

    # Get the requested timeout
    timeoutSeconds = request.args.get("timeoutSeconds", type=int)

    # If no timeout was provided
    if timeoutSeconds == None:

        # Log a warning message
        logger.warning(f"Bad request from '{request.remote_addr}' on '{request.path}'! No timeout was provided!")

        # Return a 400 - Bad Request
        return jsonify({"status": 400, "message": "Bad Request - No timeout was provided!"}), 400

    # Global
    global nextStartIndex
    global lastCompletedEndIndex
    global runningJobs
    global pendingJobs

    # State variables
    jobExpired         = False
    previousStartIndex = 0
    currentStartIndex  = 0

    # Acquire the thread lock
    with threadLock:

        # Loop through all running jobs
        for job in runningJobs.values():

            # Check if a job is expired
            if job.expired():

                # Set the expired flag to true
                jobExpired = True

                # Stop looping through the list of running jobs
                break

        # If a job expired
        if jobExpired:

            # Get the next start index before the reset
            previousStartIndex = nextStartIndex

            # Reset the the next start index to the last completed end index
            nextStartIndex = lastCompletedEndIndex

            # Get the next start index after the reset
            currentStartIndex = nextStartIndex

            # Clear job lists
            runningJobs.clear()
            pendingJobs.clear()

        # Create a new job
        job = Job(nextStartIndex, rangeSize, timeoutSeconds)

        # Add the job to the list of running jobs
        runningJobs[job.getID()] = job

        # Increase the next start index by the jobs range size
        nextStartIndex += rangeSize

    # If a job expired log an error message
    if jobExpired: logger.error(f"A running job expired! Reset the next start index from '{previousStartIndex}' to the last completed search of '{currentStartIndex}' and cleared all jobs!")

    # Log info message
    logger.info(f"Issued a new job to '{request.remote_addr}'! Job data: '{job.getData()}'.")

    # Return job data
    return jsonify(job.getData()), 200

# =================================================================================================
# Accept search results
# =================================================================================================
@server.route("/results", methods=["POST"])
@authorizeRequest
def acceptResults():

    # If the request is not JSON
    if request.is_json != True:

        # Log a warning message
        logger.warning(f"Bad request from '{request.remote_addr}' on '{request.path}'! Request is not JSON!")

        # Return a 400 - Bad Request
        return jsonify({"status": 400, "message": "Bad Request - Request is not JSON!"}), 400

    # Get results data
    resultsData = request.get_json(silent=True)

    if resultsData == None:

        # Log a warning message
        logger.warning(f"Bad request from '{request.remote_addr}' on '{request.path}'! No JSON body provided!")

        # Return a 400 - Bad Request
        return jsonify({"status": 400, "message": "Bad Request - No JSON body provided!"}), 400

    # Global
    global lastCompletedEndIndex
    global searchResults

    # Acquire the thread lock
    with threadLock:

        # Add the results data to the list of search results
        searchResults += resultsData

        # Get latest search data
        searchData = {

            "searchedUpTo": lastCompletedEndIndex,
            "results":      searchResults

        }

        # Try writing to the search data file
        try:

            # Write search data to file
            with open(configuration["search"]["filePath"], "w") as file: json.dump(searchData, file, indent=4)

        # If an exception occurs
        except Exception as exception:

            # Log an error message
            logger.error(f"Failed to write to the search data file! Exception: '{exception}'.")

            # Terminate immediately
            sys.exit(1)

    # Log a success message
    logger.success(f"Accepted new search results from {request.remote_addr}! Results data: '{resultsData}'.")

    # Return a 200 - OK
    return jsonify({"status": 200, "message": "OK - Results accepted!"}), 200

# =================================================================================================
# Complete a job
# =================================================================================================
@server.route("/job", methods=["PUT"])
@authorizeRequest
def completeJob():

    # If the request is not JSON
    if request.is_json == False:

        # Log a warning message
        logger.warning(f"Bad request from '{request.remote_addr}' on '{request.path}'! Request is not JSON!")

        # Return a 400 - Bad Request
        return jsonify({"status": 400, "message": "Bad Request - Request is not JSON!"}), 400

    # Get job data
    jobData = request.get_json(silent=True)

    if jobData == None:

        # Log a warning message
        logger.warning(f"Bad request from '{request.remote_addr}' on '{request.path}'! No JSON body provided!")

        # Return a 400 - Bad Request
        return jsonify({"status": 400, "message": "Bad Request - No JSON body provided!"}), 400

    # If job data does not contain an ID
    if "id" not in jobData:

        # Log a warning message
        logger.warning(f"Bad request from '{request.remote_addr}' on '{request.path}'! Job data does not contain an ID!")

        # Return a 400 - Bad Request
        return jsonify({"status": 400, "message": "Bad Request - Job data does not contain an ID!"}), 400

    # Global
    global lastCompletedEndIndex
    global runningJobs
    global pendingJobs
    global searchResults

    # Set job state flags to false
    jobWasRunning = False
    jobCompleted  = False

    # Acquire the thread lock
    with threadLock:

        # If the job ID is in the list of running jobs
        if jobData["id"] in runningJobs:

            # Remove the job from the list of running jobs
            job = runningJobs.pop(jobData["id"])

            # Add the job to the list of pending jobs
            pendingJobs[jobData["id"]] = job

            # Set the job was running flag to true
            jobWasRunning = True

            # Loop unit there is no more pending job in order
            while True:

                # Set the next job in order to none
                nextJobInOrder = None

                # Loop through the list of pending jobs
                for job in pendingJobs.values():

                    # If this job is the next in order
                    if job.getStartIndex() == lastCompletedEndIndex:

                        # Set the next job in order to this job
                        nextJobInOrder = job.getID()

                        # Stop looping through the list of pending jobs
                        break

                # If there is no more job in order
                if nextJobInOrder == None:

                    # Break the loop
                    break

                # If there is a pending job in order
                else:

                    # Remove the job from the list of pending jobs
                    job = pendingJobs.pop(nextJobInOrder)

                    # Update the last completed end index to the jobs end index
                    lastCompletedEndIndex = job.getEndIndex()

                    # Set the job completed flag to true
                    jobCompleted = True

            # If a job was completed
            if jobCompleted:

                # Get latest search data
                searchData = {

                    "searchedUpTo": lastCompletedEndIndex,
                    "results":      searchResults

                }

                # Try writing to the search data file
                try:

                    # Write search data to file
                    with open(configuration["search"]["filePath"], "w") as file: json.dump(searchData, file, indent=4)

                # If an exception occurs
                except Exception as exception:

                    # Log an error message
                    logger.error(f"Failed to write to the search data file! Exception: '{exception}'.")

                    # Terminate immediately
                    sys.exit(1)

    # If job was not running
    if jobWasRunning == False:

        # Log a warning message
        logger.warning(f"Bad request from '{request.remote_addr}' on '{request.path}'! Job '{jobData["id"]}' is not running!")

        # Return a 400 - Bad Request
        return jsonify({"status": 400, "message": f"Bad Request - Job '{jobData["id"]}' is not running!"}), 400

    # Log an info message
    logger.info(f"Received a completed job from '{request.remote_addr}'! Job data: '{jobData}'.")

    # Return 200 - OK
    return jsonify({"status": 200, "message": "OK - Job completed!"}), 200

# =================================================================================================
# Get status
# =================================================================================================
@server.route("/status", methods=["GET"])
def getStatus():

    # Acquire thread lock
    with threadLock:

        # Calculate additional values
        searchesProcessed = lastCompletedEndIndex - loadedStartIndex
        upTimeSeconds     = time.time() - startTime
        searchesPerHour   = searchesProcessed / (upTimeSeconds / 3600)

        # Construct status data
        statusData = {

            "nextSearch":        nextStartIndex,
            "searchedUpTo":      lastCompletedEndIndex,
            "runningJobs":       len(runningJobs),
            "pendingJobs":       len(pendingJobs),
            "searchResults":     len(searchResults),
            "searchesProcessed": searchesProcessed,
            "upTimeSeconds":     round(upTimeSeconds),
            "searchesPerHour":   round(searchesPerHour)

        }

    # Log info message
    logger.info(f"New status request from '{request.remote_addr}'. Status data: '{statusData}'")

    # Return status data
    return jsonify(statusData), 200

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

        "server": {

            "host":   "0.0.0.0",
            "port":   5000,
            "apiKey": "API-Key"

        },

        "logger": {

            "filePath": "./server.log",
            "debug":    True,
            "info":     True,
            "success":  True,
            "warning":  True,
            "error":    True

        },

        "search": {

            "filePath": "./search.json"

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

    # Try loading the search data
    try:

        # Get empty search data
        search = {

            "searchedUpTo": 0,
            "results":      []

        }

        # Try loading the search data
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

    # Set search data
    threadLock            = threading.Lock()
    nextStartIndex        = search["searchedUpTo"]
    lastCompletedEndIndex = search["searchedUpTo"]
    runningJobs           = {}
    pendingJobs           = {}
    searchResults         = search["results"]
    loadedStartIndex      = search["searchedUpTo"]
    startTime             = time.time()

    # Log info message
    logger.info(f"Initialized search with a start index of '{nextStartIndex}'!")

    # Log a info message
    logger.info(f"Started server on '{configuration["server"]["host"]}:{configuration["server"]["port"]}'!")

    # Start flask server
    server.run(host=configuration["server"]["host"], port=configuration["server"]["port"])