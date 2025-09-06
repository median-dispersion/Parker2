import time

class Job:

    # ---------------------------------------------------------------------------------------------
    # Public

    # =============================================================================================
    # Initialization
    # =============================================================================================
    def __init__(self, startIndex, rangeSize, timeoutSeconds):

        # Initialize member variables
        self._id             = Job._id
        self._startIndex     = startIndex
        self._endIndex       = startIndex + rangeSize
        self._rangeSize      = rangeSize
        self._timeoutSeconds = timeoutSeconds
        self._startTime      = time.time()

        # Increase class wide ID counter by 1
        Job._id += 1

    # =============================================================================================
    # Check if the job is expired
    # =============================================================================================
    def expired(self):

        return time.time() - self._startTime >= self._timeoutSeconds

    # =============================================================================================
    # Getter functions
    # =============================================================================================
    def getID(self):             return self._id
    def getStartIndex(self):     return self._startIndex
    def getEndIndex(self):       return self._endIndex
    def getRangeSize(self):      return self._rangeSize
    def getTimeoutSeconds(self): return self._timeoutSeconds
    def getStartTime(self):      return self._startTime

    # =============================================================================================
    # Get job data
    # =============================================================================================
    def getData(self):

        return {

            "id":             self.getID(),
            "startIndex":     self.getStartIndex(),
            "endIndex":       self.getEndIndex(),
            "rangeSize":      self.getRangeSize(),
            "timeoutSeconds": self.getTimeoutSeconds(),
            "startTime":      self.getStartTime()

        }

    # ---------------------------------------------------------------------------------------------
    # Private

    _id = 0 # Class wide ID counter

# Expose the Job class
__all__ = ["Job"]