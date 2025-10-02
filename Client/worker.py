from configuration import configuration
import threading
import time
import requests
import json
import subprocess

_serverAddress = f"{configuration['server']['protocol']}://{configuration['server']['host']}:{configuration['server']['port']}"

class Worker(threading.Thread):

    # ---------------------------------------------------------------------------------------------
    # Public

    # =============================================================================================
    # Initialization
    # =============================================================================================
    def __init__(self, outputQueue):

        # Call parent class initializer
        super().__init__()

        # Initialize member variables
        self._id                       = Worker._id
        self._stopEvent                = threading.Event()
        self._outputQueue              = outputQueue
        self._lastRequestTimestamp     = 0
        self._searchProcess            = None

        # Initialize as stopped
        self._stopEvent.set()

        # Increase class wide ID counter by 1
        Worker._id += 1

    # =============================================================================================
    # Start the worker thread
    # =============================================================================================
    def start(self):

        # If not already running
        if self._stopEvent.is_set():

            # Clear the stop event
            self._stopEvent.clear()

            # run()
            super().start()

    # =============================================================================================
    # Stop the worker thread
    # =============================================================================================
    def stop(self):

        # If not already stopped
        if not self._stopEvent.is_set():

            # Set the stop event
            self._stopEvent.set()

            # Stop the search process
            self._stopSearch()

    # =============================================================================================
    # Main worker loop
    # =============================================================================================
    def run(self):

        # Loop until stopped
        while not self._stopEvent.is_set():

            # Job configuration
            jobConfiguration = None

            # Loop until successfully received a job configuration from the server or stopped
            while jobConfiguration is None and not self._stopEvent.is_set():

                # Get job configuration from server
                jobConfiguration = self._request(f"{_serverAddress}/configuration/job")

                # If successfully received the job configuration
                if jobConfiguration is not None:

                    # Set the job configuration variables
                    jobTargetDurationSeconds = jobConfiguration["targetDurationSeconds"]
                    jobUpdateIntervalSeconds = jobConfiguration["updateIntervalSeconds"]

            # Job status
            jobStatus = True

            # Next batch size
            nextBatchSize = 1

            # Loop until the jobs status is in the failed state or stopped
            while jobStatus is not None and not self._stopEvent.is_set():

                # Get a new job from the server
                job = self._request(f"{_serverAddress}/job?batchSize={nextBatchSize}")

                # If successfully received a new job from the server
                if job is not None:

                    # Output info
                    self._output("info", f"Received job '{job['id']}' starting at '{job['startIndex']}', ending at '{job['endIndex']}', with a batch size of '{job['batchSize']}'!")

                    # Work on the job
                    durationSeconds, results = self._work(job, jobUpdateIntervalSeconds)

                    # Update the job status
                    jobStatus = durationSeconds

                    # Check if job completed successfully based on the job duration
                    if durationSeconds is not None:

                        # Check if the job returned any results
                        if results is not None:

                            # Output results
                            self._output("results", results)

                            # Send the results to the server and update the job status
                            jobStatus = self._request(f"{_serverAddress}/results", "POST", results)

                        # Check the job status
                        if jobStatus is not None:

                            # Send the completed job back to the server and update the job status
                            jobStatus = self._request(f"{_serverAddress}/job/{job['id']}", "POST", job)

                        # Check the job status
                        if jobStatus is not None:

                            # Check if the job was processed faster than the target duration
                            if durationSeconds < jobTargetDurationSeconds:

                                # Scale up the next batch size accordingly clamped to a max of 2x the size of the last batch
                                nextBatchSize = round(min(jobTargetDurationSeconds / durationSeconds, 2) * nextBatchSize)

                            # If the job to longer to process than the target duration
                            else:

                                # Scale down the next batch size accordingly clamped to a batch size of at least 1
                                nextBatchSize = max(round(jobTargetDurationSeconds / durationSeconds * nextBatchSize), 1)

                            # Output info
                            self._output("info", f"Completed job '{job['id']}' in '{round(durationSeconds)}' seconds!")

    # ---------------------------------------------------------------------------------------------
    # Private

    # Class wide ID
    _id = 0

    # =============================================================================================
    # Output to the queue
    # =============================================================================================
    def _output(self, event, data):

        # Add data to the queue
        self._outputQueue.put({

            "id":    self._id,
            "event": event,
            "data":  data

        })

    # =============================================================================================
    # Perform a request
    # =============================================================================================
    def _request(self, url, method = "GET", body = None):

        # Try performing a request
        try:

            # If request delay has not been reached
            if time.time() - self._lastRequestTimestamp < configuration["server"]["request"]["delaySeconds"]:

                # Delay request
                time.sleep(configuration["server"]["request"]["delaySeconds"])

            # Capture new request timestamp
            self._lastRequestTimestamp = time.time()

            # Construct headers
            headers = {

                "Content-Type":  "application/json",
                "Authorization": f"Bearer {configuration['server']['apiKey']}"

            }

            # Perform request depending on method
            if method == "GET":    response = requests.get   (url, headers=headers,            timeout=configuration["server"]["request"]["timeoutSeconds"])
            if method == "POST":   response = requests.post  (url, headers=headers, json=body, timeout=configuration["server"]["request"]["timeoutSeconds"])
            if method == "PUT":    response = requests.put   (url, headers=headers, json=body, timeout=configuration["server"]["request"]["timeoutSeconds"])
            if method == "DELETE": response = requests.delete(url, headers=headers,            timeout=configuration["server"]["request"]["timeoutSeconds"])

            # Raise exception if not 200 OK
            response.raise_for_status()

            # Return parsed JSON data
            return response.json()

        # If an exception occurs
        except Exception as exception:

            # Output error
            self._output("error", f"Failed to perform '{method}' request on '{url}'! Exception: '{exception}'.")

            # Return no data
            return None

    # =============================================================================================
    # Work on a job
    # =============================================================================================
    def _work(self, job, updateIntervalSeconds):

        # Try working on a job
        try:

            # Capture the job start timestamp
            startTimestamp = time.time()

            # Start the search process
            self._searchProcess = subprocess.Popen(

                [
                    str(configuration["search"]["binaryPath"]),
                    str(job["startIndex"]),
                    str(job["endIndex"])
                ],

                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True

            )

            # Last job update timestamp
            lastUpdateTimestamp = 0

            # Loop while the search process is running
            while self._searchProcess.poll() is None:

                # Avoid busy waiting
                time.sleep(0.1)

                # If the job update interval has been reached
                if time.time() - lastUpdateTimestamp >= updateIntervalSeconds:

                    # Capture the job update timestamp
                    lastUpdateTimestamp = time.time()

                    # Send a job update to the server
                    if self._request(f"{_serverAddress}/job/{job['id']}", "PUT", job) is None:

                        # Raise and exception if the job update failed
                        raise Exception("Failed to send job update!")

            # Calculate job duration
            durationSeconds = time.time() - startTimestamp

            # Get the output from the search binary
            output, error = self._searchProcess.communicate()

            # Check if the search process exited with an error code
            if self._searchProcess.returncode != 0:

                # Raise an exception
                raise subprocess.CalledProcessError(

                    self._searchProcess.returncode,

                    [
                        str(configuration["search"]["binaryPath"]),
                        str(job["startIndex"]),
                        str(job["endIndex"])
                    ],

                    output,
                    error

                )

            # List of job results
            results = []

            # Loop through every line in the output
            for line in output.splitlines():

                # Parse the output as JSON and add it to the list of results
                results.append(json.loads(line.strip()))

            # Return job duration and results if there are any
            return (durationSeconds, results) if results else (durationSeconds, None)

        # If an exception occurs
        except Exception as exception:

            # Stop the search process
            self._stopSearch()

            # Output error
            self._output("error", f"Failed to complete search on job '{job['id']}'! Exception: '{exception}'.")

            # Return no data
            return (None, None)

    # =============================================================================================
    # Stop a running search process
    # =============================================================================================
    def _stopSearch(self):

        # Check if the search process is currently running
        if self._searchProcess is not None and self._searchProcess.poll() is None:

            # Kill the search process
            self._searchProcess.kill()

# Expose the Worker class
__all__ = ["Worker"]