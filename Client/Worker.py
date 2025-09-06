import threading
import time
import requests
import subprocess
import json
import math

class Worker(threading.Thread):

    # ---------------------------------------------------------------------------------------------
    # Public

    # =============================================================================================
    # Initialization
    # =============================================================================================
    def __init__(
        self,
        workerID,
        reportQueue,
        serverAddress,
        apiKey,
        requestDelaySeconds,
        requestTimeoutSeconds,
        searchBinaryPath,
        targetSearchDurationSeconds,
        jobTimeoutFactor
    ):

        super().__init__()

        # Initialize member variables 
        self._id                          = workerID
        self._reportQueue                 = reportQueue
        self._serverAddress               = serverAddress
        self._apiKey                      = apiKey
        self._requestDelaySeconds         = requestDelaySeconds
        self._requestTimeoutSeconds       = requestTimeoutSeconds
        self._searchBinaryPath            = searchBinaryPath
        self._targetSearchDurationSeconds = targetSearchDurationSeconds
        self._jobTimeoutFactor            = jobTimeoutFactor
        self._stopEvent                   = threading.Event()
        self._lastRequestTime             = 0
        self._searchProcess               = None
        self._jobRangeSize                = None
        self._jobTimeoutSeconds           = None
        self._jobRangeSizeScaleUpFactor   = 1.2
        self._minimumJobTimeoutSeconds    = int(math.ceil(self._targetSearchDurationSeconds * self._jobTimeoutFactor))

    # =============================================================================================
    # Stop the worker thread
    # =============================================================================================
    def stop(self):

        # Set the stop event
        self._stopEvent.set()

        # Stop the search process
        self._stopSearch()

    # =============================================================================================
    # Start the worker thread
    # =============================================================================================
    def run(self):

        # While not stopped
        while not self._stopEvent.is_set():

            # Report worker start
            self._report("status", f"Worker '{self._id}' started!")

            # Reset parameters
            self._jobRangeSize      = None
            self._jobTimeoutSeconds = None
            jobCompleted            = False

            # Get the latest search status from the server
            status = self._getData(f"http://{self._serverAddress}/status")

            # If successfully gotten the search status
            if status != None:

                # Report the search status
                self._report("status", f"Worker '{self._id}' got the latest search status information! Status: '{status}'.")

                # Construct a dry run based on the next search index
                startIndex = status["nextSearch"]
                endIndex   = status["nextSearch"] + 1
                rangeSize  = endIndex - startIndex

                # Perform the dry run
                executionTimeSeconds = self._startSearch(startIndex, endIndex)
                
                # If the dry run completed without errors
                if executionTimeSeconds != None:

                    # Calculate next job range size and timeout base on the number of searches per second
                    searchesPerSecond       = rangeSize / executionTimeSeconds
                    self._jobRangeSize      = int(max(math.ceil(searchesPerSecond * self._targetSearchDurationSeconds), 1))
                    self._jobTimeoutSeconds = int(max(math.ceil((self._jobRangeSize / searchesPerSecond) * self._jobTimeoutFactor), self._minimumJobTimeoutSeconds))
                    jobCompleted            = True

                    # Report dry run completion
                    self._report("status", f"Worker '{self._id}' completed a dry run! Next job range size will be '{self._jobRangeSize}' with a timeout of '{self._jobTimeoutSeconds}' seconds.")

            # While last job completed successfully and not stopped
            while jobCompleted and not self._stopEvent.is_set():

                # Set the last job completed flag to false
                jobCompleted = False

                # Get a new job with a given range size and timeout
                job = self._getData(f"http://{self._serverAddress}/job?rangeSize={self._jobRangeSize}&timeoutSeconds={self._jobTimeoutSeconds}")

                # If successfully gotten a new job
                if job != None:
                    
                    # Report job data
                    self._report("status", f"Worker '{self._id}' got new job! Job data: '{job}'.")

                    # Perform a search
                    executionTimeSeconds = self._startSearch(job["startIndex"], job["endIndex"], job["timeoutSeconds"])

                    # If search completed without errors
                    if executionTimeSeconds != None:

                        # Send job completion to server
                        sent = self._sendData(f"http://{self._serverAddress}/job", job, "PUT")

                        # If job completion was successfully sent to server
                        if sent == True:

                            # Calculate the next estimated job range size based on the number of searches per second
                            searchesPerSecond = job["rangeSize"] / executionTimeSeconds
                            nextJobRangeSize  = searchesPerSecond * self._targetSearchDurationSeconds

                            # If the last search execution time took longer than the target search duration
                            if executionTimeSeconds > self._targetSearchDurationSeconds:
                                
                                # Scale down the next job range size by the duration overshoot percentage
                                jobRangeSizeScaleDownFactor = (1 / executionTimeSeconds) * self._targetSearchDurationSeconds
                                self._jobRangeSize          = nextJobRangeSize * jobRangeSizeScaleDownFactor

                            # If the last search execution time was shorter than the target search duration
                            else:

                                # Calculate the next maximum job range size based on the job range scale up factor
                                maximumNextJobRangeSize = job["rangeSize"] * self._jobRangeSizeScaleUpFactor

                                # If the next estimated job range size is lager than the maximum use the maximum, else use the next next estimated job range size
                                if nextJobRangeSize > maximumNextJobRangeSize: self._jobRangeSize = maximumNextJobRangeSize
                                else:                                          self._jobRangeSize = nextJobRangeSize

                            # Set the job range size and timeout to the new calculated value, ensure they are integers
                            self._jobRangeSize      = int(max(math.ceil(self._jobRangeSize), 1))
                            self._jobTimeoutSeconds = int(max(math.ceil((self._jobRangeSize / searchesPerSecond) * self._jobTimeoutFactor), self._minimumJobTimeoutSeconds))
                            jobCompleted            = True

                            # Report job completion
                            self._report("status", f"Worker '{self._id}' completed a job! Job data: '{job}'. Next job range size will be '{self._jobRangeSize}' with a timeout of '{self._jobTimeoutSeconds}' seconds.")

    # ---------------------------------------------------------------------------------------------
    # Private

    # =============================================================================================
    # Report a message to the queue
    # =============================================================================================
    def _report(self, category, message, data=None):

        # Create a new report
        report = {

            "category": category,
            "message":  message

        }

        # Add data to the report if provided
        if data != None: report["data"] = data

        # Add the report to the report queue
        self._reportQueue.put(report)

    # =============================================================================================
    # Get data from the server
    # =============================================================================================
    def _getData(self, url):

        # Check if the request delay has been reached, if not delay request
        if time.time() - self._lastRequestTime < self._requestDelaySeconds: time.sleep(self._requestDelaySeconds)

        # Capture the last request time
        self._lastRequestTime = time.time()

        # Construct headers
        headers = {

            "Content-Type":  "application/json",
            "Authorization": f"Bearer {self._apiKey}"

        }

        # Try performing a request
        try:

            # Perform request
            response = requests.get(url, headers=headers, timeout=self._requestTimeoutSeconds)

            # Raise exception if not 200 OK
            response.raise_for_status()

            # Return parsed JSON data
            return response.json()

        # If an exception occurs
        except Exception as exception:

            # Report exception
            self._report("exception", f"Worker '{self._id}' failed to get data from '{url}'! Exception: '{exception}'.")

            # Return no request data
            return None

    # =============================================================================================
    # Send data to the server
    # =============================================================================================
    def _sendData(self, url, data, method="PUT"):

        # Check if the request delay has been reached, if not delay request
        if time.time() - self._lastRequestTime < self._requestDelaySeconds: time.sleep(self._requestDelaySeconds)

        # Capture the last request time
        self._lastRequestTime = time.time()

        # Construct headers
        headers = {

            "Content-Type":  "application/json",
            "Authorization": f"Bearer {self._apiKey}"

        }

        # Try performing a request
        try:

            # Use either PUT or POST to perform the request
            if method == "PUT": response = requests.put(url, headers=headers, json=data, timeout=self._requestTimeoutSeconds)
            else:               response = requests.post(url, headers=headers, json=data, timeout=self._requestTimeoutSeconds)

            # Raise exception if not 200 OK
            response.raise_for_status()

            # Return that the data was sent
            return True

        # If an exception occurs
        except Exception as exception:

            # Report exception
            self._report("exception", f"Worker '{self._id}' failed to send data to '{url}'! Exception: '{exception}'.")

            # Return that data was not sent
            return False

    # =============================================================================================
    # Stop the search
    # =============================================================================================
    def _stopSearch(self):

        # Check if the search process is running
        if self._searchProcess != None and self._searchProcess.poll() == None:

            # Kill the search process
            self._searchProcess.kill()

            # Set the search process to None
            self._searchProcess = None

    # =============================================================================================
    # Start the search
    # =============================================================================================
    def _startSearch(self, startIndex, endIndex, timeoutSeconds=None):

        # Try performing a search
        try:

            # Capture the search start time
            startTime = time.time()

            # Start the search process
            self._searchProcess = subprocess.Popen(

                [

                    str(self._searchBinaryPath),
                    str(startIndex),
                    str(endIndex)

                ],

                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True

            )

            # Wait for the search process to finish given a timeout and capture its exit code
            exitCode = self._searchProcess.wait(timeout=timeoutSeconds)

            # Calculate the search process execution time
            executionTimeSeconds = time.time() - startTime

            # If the search process did not exit cleanly i.e. a crash or kill raise an exception
            if exitCode != 0: raise Exception(f"Expected exit code '0' got exit code '{exitCode}'!")

            # Get the search output
            stdout, stderr = self._searchProcess.communicate()

            # Search results
            results = []

            # Parse every output line as JSON and append it to the search results
            for output in stdout.splitlines(): results.append(json.loads(output))

            # If there are any results
            if len(results) > 0:

                # Report the results
                self._report("results", f"Worker '{self._id}' found results! Results data: '{results}'.", results)

                # Send the results to the server
                sent = self._sendData(f"http://{self._serverAddress}/results", results, "POST")

                # Check if the results were sent, if not raise an exception
                if sent == False: raise Exception("Failed to send results data!")

            # Set the search process to None
            self._searchProcess = None

            # Return the execution time
            return executionTimeSeconds

        # If an exception occurs
        except Exception as exception:

            # Stop the search process
            self._stopSearch()

            # Report the exception
            self._report("exception", f"Worker '{self._id}' failed to complete search! Exception: {exception}.")

            # Return no execution time
            return None

# Expose the Worker class
__all__ = ["Worker"]