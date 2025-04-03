import time
import argparse
import threading
import subprocess
import os
import json

# Value at witch the search should begin
START_OFFSET = 0

# Search batch size
BATCH_SIZE = 10000

# Number of search threads (0 = auto)
NUMBER_OF_TREADS = 0

# Flag for ignoring magic squares with duplicate values inside of them
IGNORE_DUPLICATE_VALUES = 1

# Path to the search binary
SEARCH_BINARY = "./limited.out"

# Initialization ISO date string
INITIALIZATION_DATE = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime())

# Path to the work directory
WORK_DIRECTORY = f"./{INITIALIZATION_DATE}"

# Path to the log file
LOG_FILE = f"{WORK_DIRECTORY}/log_{INITIALIZATION_DATE}.json"

# Path to weights file
WEIGHTS_FILE = f"{WORK_DIRECTORY}/weights_{INITIALIZATION_DATE}.json"

# Lock for thread-safe execution
THREAD_LOCK = threading.Lock()

# Search status
STATUS = {

    "maximum": 0,
    "weights": 0

}

# =================================================================================================
# Handle launch arguments
# =================================================================================================
def handleArguments():

    # Get global variables
    global START_OFFSET, BATCH_SIZE, NUMBER_OF_TREADS, IGNORE_DUPLICATE_VALUES, SEARCH_BINARY, WORK_DIRECTORY

    # Create a parser object
    parser = argparse.ArgumentParser(description="A brute force solution to find a magic square of squares")

    # Define launch arguments
    parser.add_argument("--start",             type=int, default=START_OFFSET,            help="Start value of the search")
    parser.add_argument("--size",              type=int, default=BATCH_SIZE,              help="Batch size")
    parser.add_argument("--threads",           type=int, default=NUMBER_OF_TREADS,        help="Number of search threads")
    parser.add_argument("--ignore-duplicates", type=int, default=IGNORE_DUPLICATE_VALUES, help="Ignore magic squares with repeating values")
    parser.add_argument("--binary",            type=str, default=SEARCH_BINARY,           help="Path to the search binary")
    parser.add_argument("--directory",         type=str, default=WORK_DIRECTORY,          help="Path to the work directory")

    # Parse the command-line arguments
    arguments = parser.parse_args()

    # Apply launch arguments globally
    START_OFFSET            = arguments.start
    BATCH_SIZE              = arguments.size
    NUMBER_OF_TREADS        = arguments.threads
    IGNORE_DUPLICATE_VALUES = arguments.ignore_duplicates
    SEARCH_BINARY           = arguments.binary
    WORK_DIRECTORY          = arguments.directory

# =================================================================================================
# Write to log file
# =================================================================================================
def writeLog(message):

    # Get thread lock
    with THREAD_LOCK:

        # Append message to the log file
        with open(LOG_FILE, "a") as file: file.write(f"{message}\n")

# =================================================================================================
# Update the search status
# =================================================================================================
def updateStatus(data):

    # Get thread lock
    with THREAD_LOCK:

        # Update the highest searched value
        # !!! THIS IS NOT GOOD AND MIGHT IGNORE LOWER RANGES THAT HAVE NOT BEEN SEARCHED !!!
        # !!! ONLY TEMPORARY !!!
        if data["end"] > STATUS["maximum"]: STATUS["maximum"] = data["end"]

# =================================================================================================
# Write magic weights to a file 
# =================================================================================================
def writeMagicWeights(data):

    # Construct output JSON
    weights = {

        "date":    time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime()),
        "threadID": data["threadID"],
        "weights": data["weights"]

    }

    # Get thread lock
    with THREAD_LOCK:

        # Write magic weights to file
        with open(WEIGHTS_FILE, "a") as file: file.write(f"{json.dumps(weights)}\n")

        # Increase the weights counter
        STATUS["weights"] += 1

# =================================================================================================
# Search thread
# =================================================================================================
def search(threadID):

    # Start a subprocess of the search binary and capture the output
    # Pass threading information and search offsets as launch arguments
    process = subprocess.Popen(

        [
            SEARCH_BINARY, 
            "--start", str(START_OFFSET), 
            "--size", str(BATCH_SIZE), 
            "--id", str(threadID), 
            "--threads", str(NUMBER_OF_TREADS), 
            "--ignore-duplicates", str(IGNORE_DUPLICATE_VALUES)
        ],

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
                
                # Parse JSON
                data = json.loads(message)

                # If message is a status update
                if data["message"] == "status":

                    # Update the status
                    updateStatus(data)

                # If message is a found set of weights
                elif data["message"] == "weights":
                    
                    # Write weights to a file
                    writeMagicWeights(data)

            # Ignore any errors
            except: pass

# =================================================================================================
# Start search threads
# =================================================================================================
def startThreads():

    # Get global variables
    global NUMBER_OF_TREADS

    # Number of search threads
    numberOfThreads = 1

    # If the number of specified threads is set to auto
    if NUMBER_OF_TREADS == 0:

        # Get the number of CPU cores
        numberOfThreads = os.cpu_count()

        # Leave 1 CPU core free
        if numberOfThreads > 1: numberOfThreads -= 1

    # If a number of threads was specified
    else:

        # Use the number of specified threads
        numberOfThreads = NUMBER_OF_TREADS

    NUMBER_OF_TREADS = numberOfThreads

    # List of threads
    threads = []

    # For the number of threads
    for threadID in range(numberOfThreads):

        # Create a new thread
        thread = threading.Thread(target=search, args=(threadID,))

        # Append thread to the list of threads
        threads.append(thread)

        # Start the thread
        thread.start()


# =================================================================================================
# Format large integers
# =================================================================================================
def formatLargeInteger(value):

    # Unit strings
    units = ["", "thousand", "million", "billion", "trillion", "quadrillion", "quintillion"]

    # Selected unit string
    unit = 0

    # If the iteration count is more that 999 *Unit*
    while value >= 1000 and unit < len(units) - 1:

        # Divide to get the next unit
        value /= 1000.0

        # Increase the selected unit
        unit += 1

    # Return iterations as a formatted string
    return f"{round(value, 2)} {units[unit]}".strip()

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

            # Print status message
            print(
                f"{time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime())} >> " +
                f"Found {STATUS["weights"]} potential sets of magic weights in a search up to x = " +
                f"{formatLargeInteger(STATUS["maximum"])} ..."
            )

            # Wait 5 seconds before printing the next status message
            time.sleep(5)
    
    # Handle keyboard interrupts
    except KeyboardInterrupt: 

        # Exit
        exit()

if __name__ == "__main__": main()