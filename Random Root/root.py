import time
import threading
import argparse
import os
import subprocess
import json

# Number of search threads (0 = auto)
NUMBER_OF_TREADS = 0

# Path to the search binary
SEARCH_BINARY = "./root.out"

# Initialization ISO date string
INITIALIZATION_DATE = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime())

# Path to the work directory
WORK_DIRECTORY = f"./{INITIALIZATION_DATE}"

# Path to the log file
LOG_FILE = f"{WORK_DIRECTORY}/log_{INITIALIZATION_DATE}.json"

# Path to results file
WEIGHTS_FILE = f"{WORK_DIRECTORY}/weights_{INITIALIZATION_DATE}.json"

# Lock for thread-safe execution
THREAD_LOCK = threading.Lock()

# Status
STATUS = {

    "iterations": 0,
    "weights": 0

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

        # Add to the total number of iterations
        STATUS["iterations"] += data["iterations"]

# =================================================================================================
# 
# =================================================================================================
def writeMagicWeights(data):

    # Construct output JSON
    weights = {

        "date":    time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime()),
        "type":    data["type"],
        "weights": data["weights"]

    }

    # Get thread lock
    with THREAD_LOCK:

        # Write magic weights to file
        with open(WEIGHTS_FILE, "a") as file: file.write(json.dumps(weights) + "\n")

        # Add one to the number of found weights
        STATUS["weights"] += 1

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

                elif data["message"] == "weights":

                    writeMagicWeights(data)

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
def formatIterations(iterations):

    # Unit strings
    units = ["", "thousand", "million", "billion", "trillion", "quadrillion", "quintillion"]

    # Selected unit string
    unit = 0

    # If the iteration count is more that 999 *Unit*
    while iterations >= 1000 and unit < len(units) - 1:

        # Divide to get the next unit
        iterations /= 1000.0

        # Increase the selected unit
        unit += 1

    # Return iterations as a formatted string
    return f"{round(iterations, 2)} {units[unit]}".strip()

# =================================================================================================
# 
# =================================================================================================
def formatDuration(duration):

    # Time unit strings
    units = ["seconds", "minutes", "hours", "days", "months", "years"]

    # Selected unit string
    unit = 0

    # If the duration count is more that 60 *Time unit*
    while duration >= 60 and unit < len(units) - 1:

        # Divide to get the next time unit
        duration /= 60

        # Increase the selected unit
        unit += 1

    # Return duration as a formatted string
    return f"{round(duration, 2)} {units[unit]}".strip()

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

    # Get the loop start time
    startTime = time.time()

    # Main loop
    try:

        # Loop forever
        while True:

            # Print status message
            print(
                f"{time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime())} >> " +
                f"Found {STATUS["weights"]} potential set magic weights in " +
                f"{formatIterations(STATUS["iterations"])} iterations and took " +
                f"{formatDuration(time.time() - startTime)} " +
                f"({formatIterations((STATUS["iterations"] / (time.time() - startTime)) * 3600)} iterations per hour)..."
            )

            # Wait 5 seconds before printing the next status message
            time.sleep(5)
    
    # Handle keyboard interrupts
    except KeyboardInterrupt: 

        # Exit
        exit()

if __name__ == "__main__": main()