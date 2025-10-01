from configuration import configuration
from threading import Lock
from enum import Enum
from datetime import datetime

# ANSI escape codes
_ANSI_FOREGROUND_BRIGHT_RED     = "\033[91m"
_ANSI_FOREGROUND_BRIGHT_GREEN   = "\033[92m"
_ANSI_FOREGROUND_BRIGHT_YELLOW  = "\033[93m"
_ANSI_FOREGROUND_BRIGHT_BLUE    = "\033[94m"
_ANSI_FOREGROUND_BRIGHT_MAGENTA = "\033[95m"
_ANSI_FOREGROUND_BRIGHT_CYAN    = "\033[96m"
_ANSI_BOLD                      = "\033[1m"
_ANSI_RESET                     = "\033[0m"

class _Logger:

    # ---------------------------------------------------------------------------------------------
    # Public

    # =============================================================================================
    # Initialization
    # =============================================================================================
    def __init__(self):

        # Initialize member variables
        self._threadLock = Lock()

    # =============================================================================================
    # Log functions
    # =============================================================================================
    def debug  (self, message): self._log(self._LogLevel.DEBUG,   message)
    def info   (self, message): self._log(self._LogLevel.INFO,    message)
    def success(self, message): self._log(self._LogLevel.SUCCESS, message)
    def warning(self, message): self._log(self._LogLevel.WARNING, message)
    def error  (self, message): self._log(self._LogLevel.ERROR,   message)

    # ---------------------------------------------------------------------------------------------
    # Private

    # Log levels
    class _LogLevel(Enum):

        DEBUG   = 0
        INFO    = 1
        SUCCESS = 2
        WARNING = 3
        ERROR   = 4

    # =============================================================================================
    # Log a message
    # =============================================================================================
    def _log(self, logLevel, message):

        # Get the current date as an ISO string
        date = datetime.now().astimezone().isoformat()

        # Depending on the log level set the message category and color
        match logLevel:

            case self._LogLevel.DEBUG:
                category = "[DEBUG]"
                color    = _ANSI_FOREGROUND_BRIGHT_MAGENTA

            case self._LogLevel.INFO:
                category = "[INFO]"
                color    = _ANSI_FOREGROUND_BRIGHT_CYAN

            case self._LogLevel.SUCCESS:
                category = "[SUCCESS]"
                color    = _ANSI_FOREGROUND_BRIGHT_GREEN
            
            case self._LogLevel.WARNING:
                category = "[WARNING]"
                color    = _ANSI_FOREGROUND_BRIGHT_YELLOW

            case self._LogLevel.ERROR:
                category = "[ERROR]"
                color    = _ANSI_FOREGROUND_BRIGHT_RED

        # Acquire the thread lock
        with self._threadLock:

            # Print the log message to the terminal
            print(f"{_ANSI_FOREGROUND_BRIGHT_BLUE}{date}{_ANSI_RESET} {_ANSI_BOLD}{color}{category}{_ANSI_RESET} >> {message}")

            # Check if the log file path has been set
            if configuration["logger"]["filePath"] is not None:

                # Try writing to the log file
                try:

                    # Open the log file
                    with open(configuration["logger"]["filePath"], "a") as file:

                        # Write the log message to the file
                        file.write(f"{date} {category} >> {message}\n")

                # If an exception occurs when writing to the log file
                except Exception as exception:

                    # Print a error message
                    print(f"{_ANSI_FOREGROUND_BRIGHT_BLUE}{date}{_ANSI_RESET} {_ANSI_BOLD}{_ANSI_FOREGROUND_BRIGHT_RED}[ERROR]{_ANSI_RESET} >> Failed writing to the log file '{configuration['logger']['filePath']}'! Exception: '{exception}'.")

# Create a singleton logger instance
logger = _Logger()

# Expose the logger instance
__all__ = ["logger"]