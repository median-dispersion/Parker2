import time
import threading
import argparse
import os
import subprocess
import json

# Number of search threads (0 = auto)
NUMBER_OF_TREADS = 0

# Path to the search binary
SEARCH_BINARY = "./search.out"

# Initialization ISO date string
INITIALIZATION_DATE = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime())

# Path to the work directory
WORK_DIRECTORY = f"./{INITIALIZATION_DATE}"

# Path to the log file
LOG_FILE = f"{WORK_DIRECTORY}/log_{INITIALIZATION_DATE}.json"

# Path to results file
SQUARES_FILE = f"{WORK_DIRECTORY}/squares_{INITIALIZATION_DATE}.json"

# Lock for thread-safe execution
THREAD_LOCK = threading.Lock()

# Status
STATUS = {

    "iterations": 0,
    "durationMilliseconds": 0

}

# =================================================================================================
# Handle launch arguments
# =================================================================================================
def handleArguments():

    # Get global variables
    global NUMBER_OF_TREADS, SEARCH_BINARY, WORK_DIRECTORY

    # Create a parser object
    parser = argparse.ArgumentParser(description="A brute force solution to find a magic square of squares")

    # Define launch arguments
    parser.add_argument("--threads",   type=int, default=NUMBER_OF_TREADS, help="Number of search threads")
    parser.add_argument("--binary",    type=str, default=SEARCH_BINARY,    help="Path to the search binary")
    parser.add_argument("--directory", type=str, default=WORK_DIRECTORY,   help="Path to the work directory")

    # Parse the command-line arguments
    arguments = parser.parse_args()

    # Apply launch arguments globally
    NUMBER_OF_TREADS = arguments.threads
    SEARCH_BINARY    = arguments.binary
    WORK_DIRECTORY   = arguments.directory

# =================================================================================================
# 
# =================================================================================================
def writeLog(message):

    # Get thread lock
    with THREAD_LOCK:

        # Append message to the log file
        with open(LOG_FILE, "a") as file: file.write(message)

# =================================================================================================
# 
# =================================================================================================
def updateStatus(data):

    # Get thread lock
    with THREAD_LOCK:

        STATUS["iterations"]           += data["iterations"]
        STATUS["durationMilliseconds"] += data["durationMilliseconds"]

# =================================================================================================
# 
# =================================================================================================
def writeMagicSquare(data):

    # Construct output JSON
    square = {

        "date":   time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime()),
        "type":   data["type"],
        "values": data["values"]

    }

    # Get thread lock
    with THREAD_LOCK:

        # Write magic square to file
        with open(SQUARES_FILE, "a") as file: file.write(json.dumps(square) + "\n")

# =================================================================================================
# Search thread
# =================================================================================================
def search():

    # Start a subprocess of the search binary and capture the output
    process = subprocess.Popen(
        [SEARCH_BINARY],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )

    # Capture the output
    with process.stdout as output:

        # For every line in the output
        for line in output:

            # Strip message
            message = line.strip()

            # Write message to log file
            writeLog(message)

            # Try parsing JSON
            try:
                
                data = json.loads(message)

                if data["message"] == "status":

                    updateStatus(data)

                elif data["message"] == "square":

                    writeMagicSquare(data)

            # Ignore any errors
            except: pass

# =================================================================================================
# Start search threads
# =================================================================================================
def startThreads():

    # Number of search threads
    numberOfThread = 1

    # If the number of specified threads is set to auto
    if NUMBER_OF_TREADS == 0:

        # Get the number of CPU cores
        numberOfThread = os.cpu_count()

        # Leave 1 CPU core free
        if numberOfThread > 1: numberOfThread -= 1

    # If a number of threads was specified
    else:

        # Use the number of specified threads
        numberOfThread = NUMBER_OF_TREADS

    # List of threads
    threads = []

    # For the number of threads
    for i in range(numberOfThread):

        # Create a new thread
        thread = threading.Thread(target=search)

        # Append thread to the list of threads
        threads.append(thread)

        # Start the thread
        thread.start()

# =================================================================================================
# 
# =================================================================================================
def printStatus():

    date = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime())

# =================================================================================================
# Main function
# =================================================================================================
def main():

    # Handle launch arguments
    handleArguments()

    # Create work directory
    os.makedirs(WORK_DIRECTORY, exist_ok=True)

    # Start search threads
    startThreads()

    # Main loop
    try:

        # Loop forever
        while True:

            print( f"{STATUS["iterations"]:,} iterations in {STATUS['durationMilliseconds']} ms...".replace(',', '.') )

            time.sleep(5)
    
    # Handle keyboard interrupts
    except KeyboardInterrupt: 

        # Exit
        exit()

if __name__ == "__main__": main()