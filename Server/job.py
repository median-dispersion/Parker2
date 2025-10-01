from configuration import configuration
from logger import logger
from time import time

class Job:

    # ---------------------------------------------------------------------------------------------
    # Public

    # =============================================================================================
    # Initialization
    # =============================================================================================
    def __init__(self, startIndex, batchSize, timeoutSeconds):

        # Initialize member variables
        self._id              = Job._id
        self._startIndex      = startIndex
        self._endIndex        = startIndex + batchSize
        self._batchSize       = batchSize
        self._timeoutSeconds  = timeoutSeconds
        self._startTimestamp  = time()
        self._updateTimestamp = time()
        self._endTimestamp    = None

        # Increase class wide ID counter by 1
        Job._id += 1

    # =============================================================================================
    # Update the job
    # =============================================================================================
    def update(self):

        # Check if the job is still running
        if self._endTimestamp is None:

            # Update the timestamp
            self._updateTimestamp = time()

    # =============================================================================================
    # Finish the job
    # =============================================================================================
    def finish(self):

        # Check if the job is still running
        if self._endTimestamp is None:

            # Set the end timestamp
            self._endTimestamp = time()

    # =============================================================================================
    # Check if the job is expired
    # =============================================================================================
    def expired(self):

        # Check if the job is still running
        if self._endTimestamp is None:

            # Return if the job is expired based on the last update
            return time() - self._updateTimestamp >= self._timeoutSeconds

        # If the job is no longer running
        else:

            # Always return not expired
            return False

    # =============================================================================================
    # Getter functions
    # =============================================================================================
    def getID(self):              return self._id
    def getStartIndex(self):      return self._startIndex
    def getEndIndex(self):        return self._endIndex
    def getBatchSize(self):       return self._batchSize
    def getTimeoutSeconds(self):  return self._timeoutSeconds
    def getStartTimestamp(self):  return self._startTimestamp
    def getUpdateTimestamp(self): return self._updateTimestamp
    def getEndTimestamp(self):    return self._endTimestamp

    # =============================================================================================
    # Get job data
    # =============================================================================================
    def getData(self):

        return {

            "id":              self._id,
            "startIndex":      self._startIndex,
            "endIndex":        self._endIndex,
            "batchSize":       self._batchSize,
            "timeoutSeconds":  self._timeoutSeconds,
            "startTimestamp":  self._startTimestamp,
            "updateTimestamp": self._updateTimestamp,
            "endTimestamp":    self._endTimestamp

        }

    # ---------------------------------------------------------------------------------------------
    # Private

    _id = 0 # Class wide ID counter

# Expose the Job class
__all__ = ["Job"]