from configuration import configuration
from logger import logger
from search import search
from flask import Flask, jsonify, request

# Flask server
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

# -------------------------------------------------------------------------------------------------
# Request with authorization

# =================================================================================================
# Issue a new job
# =================================================================================================
@server.route("/job", methods=["GET"])
@authorizeRequest
def issueJob():

    # Get the requested batch size
    batchSize = request.args.get("batchSize", type=int, default=1)

    # Issue a new search job
    job = search.issueJob(batchSize)

    # Log info message
    logger.info(f"Issued job '{job['id']}' to '{request.remote_addr}' starting at '{job['startIndex']}', ending at '{job['endIndex']}', with a batch size of '{job['batchSize']}'!")

    # Return the job
    return jsonify(job), 200

# =================================================================================================
# Update a job
# =================================================================================================
@server.route("/job/<int:jobID>", methods=["PUT"])
@authorizeRequest
def updateJob(jobID):

    # Check if the job can be updated
    if search.updateJob(jobID):

        # Return that the job was successfully updated
        return jsonify({"status": 200, "message": f"OK - Successfully updated job '{jobID}'!"}), 200

    # If the job was not updated
    else:

        # Log warning message
        logger.warning(f"Failed to update job '{jobID}' from '{request.remote_addr}'! No such job ID!")

        # Return that the job was not updated
        return jsonify({"status": 400, "message": f"Bad Request - Failed to update job '{jobID}'! No such job ID!"}), 400

# =================================================================================================
# Finish a job
# =================================================================================================
@server.route("/job/<int:jobID>", methods=["POST"])
@authorizeRequest
def finishJob(jobID):

    # Check if the job can be finished
    if search.finishJob(jobID):

        # Log info message
        logger.info(f"Received finished job '{jobID}' from '{request.remote_addr}'!")

        # Return that the job was successfully finished
        return jsonify({"status": 200, "message": f"OK - Successfully finished job '{jobID}'!"}), 200

    # If the job was not finished
    else:

        # Log warning message
        logger.warning(f"Failed to finish job '{jobID}' from '{request.remote_addr}'! No such job ID!")

        # Return that the job was not finished
        return jsonify({"status": 400, "message": f"Bad Request - Failed to finish job '{jobID}'! No such job ID!"}), 400

# =================================================================================================
# Cancel a job
# =================================================================================================
@server.route("/job/<int:jobID>", methods=["DELETE"])
@authorizeRequest
def cancelJob(jobID):

    # Check if the job can be canceled
    if search.cancelJob(jobID):

        # Log warning message
        logger.warning(f"Received cancellation of job '{jobID}' from '{request.remote_addr}'!")

        # Return that the job was successfully canceled
        return jsonify({"status": 200, "message": f"OK - Successfully canceled job '{jobID}'!"}), 200

    # If the job was not canceled
    else:

        # Log warning message
        logger.warning(f"Failed to cancel job '{jobID}' from '{request.remote_addr}'! No such job ID!")

        # Return that the job was not canceled
        return jsonify({"status": 400, "message": f"Bad Request - Failed to cancel job '{jobID}'! No such job ID!"}), 400

# =================================================================================================
# Accept results
# =================================================================================================
@server.route("/results", methods=["POST"])
@authorizeRequest
def acceptResults():

    # Check if the request is invalid JSON
    if not request.is_json:

        # Log warning message
        logger.warning(f"Bad request from '{request.remote_addr}' on '{request.path}'! Request is not JSON!")

        # Return that the request is invalid JSON
        return jsonify({"status": 400, "message": f"Bad Request - Request is not JSON!"}), 400

    # Get the results
    results = request.get_json(silent=True)

    # Check if there are no results
    if results is None:

        # Log warning message
        logger.warning(f"Bad request from '{request.remote_addr}' on '{request.path}'! No valid results were provided!")

        # Return that there are no results
        return jsonify({"status": 400, "message": f"Bad Request - No valid results were provided!"}), 400

    # Check if the results are accepted
    if search.acceptResults(results):

        # Log success message
        logger.success(f"Successfully accepted results from '{request.remote_addr}'! Results data: '{results}'.")

        # Return that the results were accepted
        return jsonify({"status": 200, "message": f"OK - Successfully accepted results!"}), 200

# -------------------------------------------------------------------------------------------------
# Request without authorization

# =================================================================================================
# Get search status
# =================================================================================================
@server.route("/status", methods=["GET"])
def getStatus(): return jsonify(search.getStatus()), 200

@server.route("/status/jobs/running", methods=["GET"])
def getRunningJobs(): return jsonify(search.getRunningJobs()), 200

@server.route("/status/jobs/pending", methods=["GET"])
def getPendingJobs(): return jsonify(search.getPendingJobs()), 200

@server.route("/status/jobs/failed", methods=["GET"])
def getFailedJobs(): return jsonify(search.getFailedJobs()), 200

@server.route("/status/jobs/completed", methods=["GET"])
def getCompletedJobs(): return jsonify(search.getCompletedJobs()), 200

@server.route("/status/results", methods=["GET"])
def getResults(): return jsonify(search.getResults()), 200

@server.route("/configuration/job", methods=["GET"])
def getJobConfiguration(): return jsonify(configuration["search"]["job"]), 200

# =================================================================================================
# Main
# =================================================================================================
if __name__ == "__main__":

    # Log info message
    logger.info(f"Starting search server on 'http://{configuration['server']['host']}:{configuration['server']['port']}'...")

    # Start the search thread
    search.start()

    # Start the server
    server.run(host=configuration["server"]["host"], port=configuration["server"]["port"])