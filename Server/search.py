from configuration import configuration
from logger import logger
from job import Job
import threading
import time
import json

class _Search(threading.Thread):

    # ---------------------------------------------------------------------------------------------
    # Public

    # =============================================================================================
    # Initialization
    # =============================================================================================
    def __init__(self):

        # Call parent class initializer
        super().__init__()

        # Initialize member variables
        self._threadLock        = threading.Lock()
        self._stopEvent         = threading.Event()
        self._startTimestamp    = None
        self._initialStartIndex = 1
        self._nextStartIndex    = 1
        self._completedEndIndex = 1
        self._runningJobs       = {}
        self._pendingJobs       = {}
        self._failedJobs        = []
        self._completedJobs     = []
        self._results           = []

        # Initialize as stopped
        self._stopEvent.set()

        # Load search data
        self._loadData()

    # =============================================================================================
    # Start the search thread
    # =============================================================================================
    def start(self):

        # If not already running
        if self._stopEvent.is_set():

            # Clear the stop event
            self._stopEvent.clear()

            # Set the start timestamp
            self._startTimestamp = time.time()

            # run()
            super().start()

    # =============================================================================================
    # Stop the search thread
    # =============================================================================================
    def stop(self):

        # If not already stopped
        if not self._stopEvent.is_set():

            # Set the stop event
            self._stopEvent.set()

            # Reset the start timestamp
            self._startTimestamp = None

    # =============================================================================================
    # Main search loop
    # =============================================================================================
    def run(self):

        # Loop until stopped
        while not self._stopEvent.is_set():

            # Avoid busy waiting
            time.sleep(1)

            # Handle running jobs and get if any expired
            jobExpired = self._handleRunningJobs()

            # Handle pending jobs and get if any completed
            jobCompleted = self._handlePendingJobs()

            # If a job expired or was completed
            if jobExpired or jobCompleted:

                # Save search data
                self._saveData()

    # =============================================================================================
    # Issue a new job
    # =============================================================================================
    def issueJob(self, batchSize):

        # Acquire the thread lock
        with self._threadLock:

            # Create a new job
            job = Job(self._nextStartIndex, batchSize, configuration["search"]["job"]["timeoutSeconds"])

            # Increase the next start index by the batch size
            self._nextStartIndex += job.getBatchSize()

            # Add the job to the list of running jobs
            self._runningJobs[job.getID()] = job

            # Return the job data
            return job.getData()

    # =============================================================================================
    # Update a job
    # =============================================================================================
    def updateJob(self, jobID):

        # Acquire the thread lock
        with self._threadLock:

            # Check if the job is in the list of running jobs
            if jobID in self._runningJobs:

                # Update the job
                self._runningJobs[jobID].update()

                # Return that the jobs was updated
                return True

            # If the job is not in the list of running jobs
            else:

                # Return that the job was not updated
                return False

    # =============================================================================================
    # Finish a job
    # =============================================================================================
    def finishJob(self, jobID):

        # Acquire the thread lock
        with self._threadLock:

            # Check if the job is in the list of running jobs
            if jobID in self._runningJobs:

                # Remove the job from the list of running jobs
                job = self._runningJobs.pop(jobID)

                # Finish the job
                job.finish()

                # Add the job to the list of pending jobs
                self._pendingJobs[job.getID()] = job

                # Return that the job was finished
                return True

            # If the job is not in the list of running jobs
            else:

                # Return that the job was not finished
                return False

    # =============================================================================================
    # Cancel a job
    # =============================================================================================
    def cancelJob(self, jobID):

        # Acquire the thread lock
        with self._threadLock:

            # Check if the job is in the list of running jobs
            if jobID in self._runningJobs:

                # Remove the job from the list of running jobs
                job = self._runningJobs.pop(jobID)

                # Check if the start index of the job is smaller than the start index of the next job
                if job.getStartIndex() < self._nextStartIndex:

                    # Reset the start index of the next job to the start index of this job
                    self._nextStartIndex = job.getStartIndex()

                # Add the job data to the list of failed jobs
                self._failedJobs.append(job.getData())

                # Return that the job was canceled
                return True

            # If the job is not in the list of running jobs
            else:

                # Return that the job was not canceled
                return False

    # =============================================================================================
    # Accept results
    # =============================================================================================
    def acceptResults(self, results):

        # Acquire the thread lock
        with self._threadLock:

            # Add the results to the list of all results
            self._results.extend(results)

            # Return that the results were accepted
            return True

    # =============================================================================================
    # Getter function
    # =============================================================================================
    def getRunningJobs(self):
        with self._threadLock: return [job.getData() for job in self._runningJobs.values()]

    def getPendingJobs(self):
        with self._threadLock: return [job.getData() for job in self._pendingJobs.values()]

    def getFailedJobs(self):
        with self._threadLock: return self._failedJobs

    def getCompletedJobs(self):
        with self._threadLock: return self._completedJobs

    def getResults(self):
        with self._threadLock: return self._results

    # =============================================================================================
    # Get status data
    # =============================================================================================
    def getStatus(self):

        # Acquire the thread lock
        with self._threadLock:

            # Calculate some additional values
            runtimeSeconds     = time.time() - self._startTimestamp
            completedSearches  = self._completedEndIndex - self._initialStartIndex
            searchesPerSeconds = completedSearches / runtimeSeconds

            # Return search status
            return {

                "runtimeSeconds":     runtimeSeconds,
                "completedSearches":  completedSearches,
                "searchesPerSeconds": searchesPerSeconds,
                "nextStartIndex":     self._nextStartIndex,
                "completedEndIndex":  self._completedEndIndex,
                "runningJobsCount":   len(self._runningJobs),
                "pendingJobsCount":   len(self._pendingJobs),
                "failedJobsCount":    len(self._failedJobs),
                "completedJobsCount": len(self._completedJobs),
                "resultsCount":       len(self._results)

            }

    # ---------------------------------------------------------------------------------------------
    # Public

    # =============================================================================================
    # Load the search data
    # =============================================================================================
    def _loadData(self):

        # Try reading the search data file
        try:

            # Open ths search data file
            with open(configuration["search"]["filePath"], "r") as file:

                # Parse file as JSON
                data = json.load(file)

            # Apply search data
            self._initialStartIndex = data["index"]
            self._nextStartIndex    = data["index"]
            self._completedEndIndex = data["index"]
            self._results           = data["results"]
            self._failedJobs        = data["failed"]
            self._completedJobs     = data["completed"]

        # If the search data file was not found
        except FileNotFoundError:

            # Log warning message
            logger.warning(f"Failed loading search data from '{configuration['search']['filePath']}'! File not found! Creating new file!")

            # Create a new search data file
            self._saveData()

    # =============================================================================================
    # Save the search data
    # =============================================================================================
    def _saveData(self):

        # Acquire the thread lock
        with self._threadLock:

            # Open ths search data file
            with open(configuration["search"]["filePath"], "w") as file:

                # Write search data to file file
                json.dump({

                    "index":     self._completedEndIndex,
                    "results":   self._results,
                    "failed":    self._failedJobs,
                    "completed": self._completedJobs

                }, file, indent=4)

    # =============================================================================================
    # Handle running jobs
    # =============================================================================================
    def _handleRunningJobs(self):

        # Acquire the thread lock
        with self._threadLock:

            # Flag for checking if a job expired
            jobExpired = False

            # List of expired job IDs
            expiredJobIDs = []

            # Loop through job in the list of running jobs
            for job in self._runningJobs.values():

                # Check if the job is expired
                if job.expired():

                    # Add the job ID to the list of expired job IDs
                    expiredJobIDs.append(job.getID())

            # Loop through the list of expired job IDs
            for jobID in expiredJobIDs:

                # Remove the job from the list of running jobs
                job = self._runningJobs.pop(jobID)

                # Check if the start index of the job is smaller than the start index of the next job
                if job.getStartIndex() < self._nextStartIndex:

                    # Reset the start index of the next job to the start index of this job
                    self._nextStartIndex = job.getStartIndex()

                # Add the job data to the list of failed jobs
                self._failedJobs.append(job.getData())

                # Log error message
                logger.error(f"Job '{job.getID()}' expired! Next start index is '{self._nextStartIndex}'!")

                # Set the flag for checking if a job expired to True
                jobExpired = True

            # Return the flag for checking if a job expired
            return jobExpired

    # =============================================================================================
    # Handle pending jobs
    # =============================================================================================
    def _handlePendingJobs(self):

        # Acquire the thread lock
        with self._threadLock:

            # Flag for checking if a job was completed
            jobCompleted = False

            # ID of the next job to complete
            nextJobID = 0

            # Loop until there are no more jobs to complete
            while nextJobID is not None:

                # Reset the ID of the next job to complete
                nextJobID = None

                # Loop through the list of pending jobs
                for job in self._pendingJobs.values():

                    # Check if the start index of the job is smaller or equal to the end index of the last completed job
                    if job.getStartIndex() <= self._completedEndIndex:

                        # Set the ID of the next job to complete to the ID of this job
                        nextJobID = job.getID()

                        # Stop looping through the list of pending jobs
                        break

                # Check if there is a job to complete
                if nextJobID is not None:

                    # Remove the job from the list of pending jobs
                    job = self._pendingJobs.pop(nextJobID)

                    # Check if the start index of this job is greater than the start index of the next job
                    if job.getStartIndex() > self._nextStartIndex:

                        # Set the start index of the next job to the start index of this job
                        self._nextStartIndex = job.getStartIndex()

                    # Check if the end index of this jobs is greater than the end index of the last completed job
                    if job.getEndIndex() > self._completedEndIndex:

                        # Set the end index of the last completed job to the end index of this job
                        self._completedEndIndex = job.getEndIndex()

                    # Add the job data to the list of completed jobs
                    self._completedJobs.append(job.getData())

                    # Log info message
                    logger.info(f"Job '{job.getID()}' was completed! Completed end index is '{self._completedEndIndex}'!")

                    # Set the flag for checking if a job was completed to True
                    jobCompleted = True

            # Return the flag for checking if a job was completed
            return jobCompleted

# Create a singleton search daemon instance
search        = _Search()
search.daemon = True

# Expose the search instance
__all__ = ["search"]