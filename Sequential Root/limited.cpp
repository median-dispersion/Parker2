/*

 A | B | C
---|---|---
 D | E | F
---|---|---
 G | H | I

 A² | B² | C²
----|----|---
 D² | E² | F²
----|----|---
 G² | H² | I²

X = <value to test>
Y = A² - X²
Z = C² - X²

   A² = X² + Y   | B² = X² - Y - Z |   C² = X² + Z
-----------------|-----------------|-----------------
 D² = X² - Y + Z |     E² = X²     | F² = X² + Y - Z
-----------------|-----------------|-----------------
   G² = X² - Z   | H² = X² + Y + Z |   I² = X² - Y
 
*/

#include <cstdint>
#include <csignal>
#include <cmath>
#include <chrono>
#include <iostream>

using namespace std;

// ------------------------------------------------------------------------------------------------
// Global variables

// Value at witch the search should begin
uint64_t START_OFFSET = 0;

// Batch iteration
uint64_t BATCH = 0;

// Batch size
uint64_t BATCH_SIZE = 1000;

// Thread ID
uint16_t THREAD_ID = 0;

// Total number of threads
uint16_t NUMBER_OF_THREADS = 1;

// Flag for ignoring magic squares with duplicate values inside of them
uint8_t IGNORE_DUPLICATE_VALUES = 1;

// ================================================================================================
// Cleanup function
// ================================================================================================
void cleanup(int signal) {

    // Exit
    exit(signal);

}

// ================================================================================================
// Handle launch arguments
// ================================================================================================
void handleArguments(int arguments, char* values[]) {

    // Variable for checking if required arguments where provided
    uint8_t requirements = 0;

    // For all arguments in list
    for (int i = 1; i < arguments; ++i) {

        // Convert argument to string
        std::string argument = values[i];

        // Check if arguments match

        // Required arguments
        if (argument == "--start" && i + 1 < arguments) {

            START_OFFSET = stoll(values[i + 1]);
            i++;
            requirements++;

        } else if (argument == "--size" && i + 1 < arguments) {

            BATCH_SIZE = stoll(values[i + 1]);
            i++;
            requirements++;

        } else if (argument == "--id" && i + 1 < arguments) {

            THREAD_ID = stoll(values[i + 1]);
            i++;
            requirements++;

        } else if (argument == "--threads" && i + 1 < arguments) {

            NUMBER_OF_THREADS = stoll(values[i + 1]);
            i++;
            requirements++;
        
        // Optional arguments
        }else if (argument == "--ignore-duplicates" && i + 1 < arguments) {

            IGNORE_DUPLICATE_VALUES = stoll(values[i + 1]);
            i++;

        }

    }

    // Check if the number of required arguments was reached
    if (requirements < 4) {

        // If not print error message

        cout << "Required arguments where missing!" << endl << endl;

        cout << "Required:" << endl;
        cout << "--start START VALUE" << endl;
        cout << "--size BATCH SIZE" << endl;
        cout << "--id THREAD ID" << endl;
        cout << "--threads NUMBER OF THREADS" << endl << endl;

        cout << "Optional:" << endl;
        cout << "--ignore-duplicates 0/1" << endl;

        cleanup(1);

    }

}

// ================================================================================================
// Check if value is a perfect square
// ================================================================================================
bool isPerfectSquare(int64_t value) {

    // Negative numbers can't be perfect squares
    if (value < 0) return false;

    // Compute the square root and convert to int
    int root = static_cast<int64_t>(sqrt(value));

    // Check if squaring gives back the original number
    return root * root == value; 

}

// ================================================================================================
// Test batch for magic squares of squares
// ================================================================================================
void testBatch(uint64_t batchStart, uint64_t batchEnd) {

    // Get the square limit
    // (+7 for good luck) (and race condition prevention)
    uint64_t squareLimit = ceil(sqrt(2) * batchEnd) + 7;

    // Loop through all values for X in this batch
    for (uint64_t x = batchStart; x < batchEnd; x++) {

        // Calculate E²
        uint64_t eSquared = x * x;

        // Loop through all possible squared values for A
        for (uint64_t aValue = 0; aValue <= squareLimit; aValue++) {

            // Calculate A²
            uint64_t aSquared = aValue * aValue;

            // Calculate Y
            int64_t y = aSquared - eSquared;

            // Calculate I²
            int64_t iSquared = eSquared - y;

            // Check if Y would result in duplicate values
            // Check if Y is smaller that E²
            // Check if I² is a perfect square
            if (
                y >= IGNORE_DUPLICATE_VALUES && 
                y <= eSquared && 
                isPerfectSquare(iSquared)
            ) {

                // Loop through all possible squared values for C
                for (uint64_t cValue = 0; cValue <= squareLimit; cValue++) {

                    // Calculate C²
                    uint64_t cSquared = cValue * cValue;

                    // Calculate Z
                    int64_t z = cSquared - eSquared;

                    // Calculate G²
                    int64_t gSquared = eSquared - z;

                    // Check if Z would result in duplicate values
                    // Check if Z is smaller that E²
                    // Check if G² is a perfect square
                    if (
                        z >= IGNORE_DUPLICATE_VALUES && 
                        z <= eSquared && 
                        isPerfectSquare(gSquared)
                    ) {

                        // Calculate remaining squares
                        int64_t bSquared = eSquared - y - z;
                        int64_t dSquared = eSquared - y + z;
                        int64_t fSquared = eSquared + y - z;
                        int64_t hSquared = eSquared + y + z;

                        // Check if all remaining values a perfect squares
                        if (
                            isPerfectSquare(bSquared) && 
                            isPerfectSquare(dSquared) && 
                            isPerfectSquare(fSquared) && 
                            isPerfectSquare(hSquared)
                        ) {

                            // Print weights as JSON
                            cout << "{\"message\":\"weights\", "
                            << "\"threadID\":" << THREAD_ID << ", "
                            << "\"weights\":{"
                            << "\"x\":" << x << ", "
                            << "\"y\":" << y << ", "
                            << "\"z\":" << z << "}}" << endl;

                        }

                    }

                }

            }

        }

    }

}

// ================================================================================================
// Main function
// ================================================================================================
int main(int arguments, char* values[]) {

    // Register interrupt signal handler
    signal(SIGINT, cleanup);

    // Register termination signal handler
    signal(SIGTERM, cleanup);

    // Handle launch arguments
    handleArguments(arguments, values);

    // Increase batch count be thread id
    BATCH += THREAD_ID;

    // Loop forever
    while (true) {

        // Record batch start time
        auto start = chrono::high_resolution_clock::now();

        // Get the batch start value
        uint64_t batchStart = (BATCH * BATCH_SIZE) + START_OFFSET;

        // Get the batch end value
        uint64_t batchEnd = ((BATCH + 1) * BATCH_SIZE) + START_OFFSET;

        // Test batch for magic squares of squares
        testBatch(batchStart, batchEnd);

        // Record batch end time
        auto end = chrono::high_resolution_clock::now();

        // Compute duration in milliseconds
        chrono::duration<double, milli> duration = end - start;

        cout << "{\"message\":\"status\", "
        << "\"threadID\":" << THREAD_ID << ", "
        << "\"start\":" << batchStart << ", "
        << "\"end\":" << batchEnd << ", "
        << "\"durationMilliseconds\":" << static_cast<uint64_t>(duration.count()) << "}" << endl;

        // Increase the batch count
        BATCH += NUMBER_OF_THREADS;

    }

    // Exit
    cleanup(0);
    
    return 0;

}