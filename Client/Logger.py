from enum import Enum
from threading import Lock
from datetime import datetime

# ANSI escape codes
_ANSI_RED     = "\033[91m"
_ANSI_GREEN   = "\033[92m"
_ANSI_YELLOW  = "\033[93m"
_ANSI_BLUE    = "\033[94m"
_ANSI_MAGENTA = "\033[95m"
_ANSI_CYAN    = "\033[96m"
_ANSI_BOLD    = "\033[1m"
_ANSI_RESET   = "\033[0m"

class _Logger:

    # ---------------------------------------------------------------------------------------------
    # Public

    # Log levels
    class Level(Enum):

        DEBUG   = 0
        INFO    = 1
        SUCCESS = 2
        WARNING = 3
        ERROR   = 4

    # =============================================================================================
    # Initialization
    # =============================================================================================
    def __init__(self):

        # Initialize member variables
        self._lock     = Lock()
        self._levels   = [True] * len(self.Level)
        self._filePath = None

    # =============================================================================================
    # Set a log level state
    # =============================================================================================
    def setLevel(self, level, state):

        # Acquire the thread lock
        with self._lock:

            # Set the log level state
            self._levels[level.value] = state

    # =============================================================================================
    # Set the log file path
    # =============================================================================================
    def setFilePath(self, filePath):

        # Acquire the thread lock
        with self._lock:

            # Set the log filePath path
            self._filePath = filePath

    # =============================================================================================
    # Log functions
    # =============================================================================================
    def debug  (self, message): self._log(self.Level.DEBUG,   message)
    def info   (self, message): self._log(self.Level.INFO,    message)
    def success(self, message): self._log(self.Level.SUCCESS, message)
    def warning(self, message): self._log(self.Level.WARNING, message)
    def error  (self, message): self._log(self.Level.ERROR,   message)

    # ---------------------------------------------------------------------------------------------
    # Private

    # =============================================================================================
    # Log a message
    # =============================================================================================
    def _log(self, level, message):

        # If log level is enabled
        if (self._levels[level.value] == True):

            # Get the current date as an ISO string
            date = datetime.now().astimezone().isoformat()

            # Depending on the log level set the message category and color
            match level:

                case self.Level.DEBUG:
                    category = "[DEBUG]"
                    color    = _ANSI_MAGENTA

                case self.Level.INFO:
                    category = "[INFO]"
                    color    = _ANSI_CYAN

                case self.Level.SUCCESS:
                    category = "[SUCCESS]"
                    color    = _ANSI_GREEN

                case self.Level.WARNING:
                    category = "[WARNING]"
                    color    = _ANSI_YELLOW

                case self.Level.ERROR:
                    category = "[ERROR]"
                    color    = _ANSI_RED

            # Acquire the thread lock
            with self._lock:

                # Print the log message to the terminal
                print(f"{_ANSI_BLUE}{date}{_ANSI_RESET} {_ANSI_BOLD}{color}{category}{_ANSI_RESET} >> {message}")

                # If the log filePath has been set
                if self._filePath != None:

                    # Try writing to the log file
                    try:

                        # Open the log filePath
                        with open(self._filePath, "a") as filePath:

                            # Write the log message to the filePath
                            filePath.write(f"{date} {category} >> {message}\n")

                    # If an exception occurs while writing to the log file
                    except Exception as exception:

                        # Print an error message
                        print(f"{_ANSI_BLUE}{date}{_ANSI_RESET} {_ANSI_BOLD}{_ANSI_RED}[LOGGER ERROR]{_ANSI_RESET} >> Could not write to log file '{self._filePath}'! Exception: '{exception}'.")

# Logger object
logger = _Logger()

# Only expose the logger object
__all__ = ["logger"]