/* 

    A naive approach for finding a 3x3 magic square of squares.

    This program generates a set of 9 unique random numbers and squares them.
    It then checks if those 9 squared values would make up a valid magic square (https://en.wikipedia.org/wiki/Magic_square).
    It does this forever, regularly printing status messages.

    The main goal is speed, to check as many combinations as possible.
    Therefore, no logic for keeping track of already checked solutions is implemented.
    With A LOT OF time and luck, this might eventually find a valid solution.

    For the main calculations, the GMP library is used.
    This library provides integers with arbitrary precision / length.

    Lower and upper bounds for the search range, i.e., the minimum and maximum number that should be squared, can be set with SEARCH_RANGE_MINIMUM and SEARCH_RANGE_MAXIMUM.
    The batch size of how many calculations will be performed in each loop can be adjusted with BATCH_SIZE.

*/

#include <cstdint>
#include <gmp.h>
#include <csignal>
#include <string>
#include <random>
#include <iostream>
#include <chrono>

using namespace std;

// ------------------------------------------------------------------------------------------------
// Global variables

// Search parameters
const uint64_t SEARCH_RANGE_MINIMUM = 0;
const uint64_t SEARCH_RANGE_MAXIMUM = 1000;
const uint64_t BATCH_SIZE           = 1000000;
const uint8_t  LOG_SQUARE_TYPE      = 10;

// GMP integers
mpz_t 
    VALUE0,
    VALUE1,
    VALUE2,
    VALUE3,
    VALUE4,
    VALUE5,
    VALUE6,
    VALUE7,
    VALUE8,
    SQUARE0,
    SQUARE1,
    SQUARE2,
    SQUARE3,
    SQUARE4,
    SQUARE5,
    SQUARE6,
    SQUARE7,
    SQUARE8,
    ROW0,
    ROW1,
    ROW2,
    COLUMN0,
    COLUMN1,
    DIAGONAL0,
    DIAGONAL1
;

// ================================================================================================
// Cleanup function
// ================================================================================================
void cleanup(int signal) {

    // Clear up the allocated memory
    mpz_clears(
        VALUE0,
        VALUE1,
        VALUE2,
        VALUE3,
        VALUE4,
        VALUE5,
        VALUE6,
        VALUE7,
        VALUE8,
        SQUARE0,
        SQUARE1,
        SQUARE2,
        SQUARE3, 
        SQUARE4,
        SQUARE5,
        SQUARE6,
        SQUARE7,
        SQUARE8,
        ROW0,
        ROW1,
        ROW2,
        COLUMN0,
        COLUMN1,
        DIAGONAL0,
        DIAGONAL1,
        NULL
    );

    // Exit
    exit(signal);

}

// ================================================================================================
// Get a set of 9 unique random values
// ================================================================================================
void getValues(uniform_int_distribution<uint64_t> &distribution, mt19937 &generator, uint64_t *values) {

    // Number of unique values
    uint8_t unique = 0;

    // Loop unit 9 unique values are generated
    while (unique < 9) {

        // Get a random number in the search range
        uint64_t number = distribution(generator);

        // Variable for checking if the array already contains the value
        bool contains = false;

        // For all elements in the array of values
        for (uint8_t value = 0; value < 9; value++) {

            // If the value is already in the array
            if (values[value] == number) {

                // Set the contains flag to true
                contains = true;

                // Break the loop immediately
                break;

            }

        }

        // If the array doesn't contain the value, i.e., it's unique
        if (!contains) {

            // Add the unique value to the array
            values[unique] = number;

            // Increase the number of unique values
            unique++;

        }

    }

}

// ================================================================================================
// Log a found square
// ================================================================================================
void logMagicSquare(uint16_t type, uint64_t *values) {

    // Only log result if magic square is of certain type
    if (type <= LOG_SQUARE_TYPE) {

        // Print the result as JSON
        cout << "{\"message\":\"square\",\"type\":" << type << ",\"values\":[";

        // For each value
        for (uint8_t value = 0; value < 9; value++) {

            // Add the value to the JSON array
            cout << values[value];

            // If not the last value add a ","
            if (value + 1 < 9) {

                cout << ",";

            }

        }

        // Add trailing "]}"
        cout << "]}" << endl;

    }

}

// ================================================================================================
// Try calculating the magic square of squares
// ================================================================================================
void calculateMagicSquare(uint64_t *values) {

    // Convert uint64_t values to values with arbitrary precision
    mpz_set_ui(VALUE0, values[0]);
    mpz_set_ui(VALUE1, values[1]);
    mpz_set_ui(VALUE2, values[2]);
    mpz_set_ui(VALUE3, values[3]);
    mpz_set_ui(VALUE4, values[4]);
    mpz_set_ui(VALUE5, values[5]);
    mpz_set_ui(VALUE6, values[6]);
    mpz_set_ui(VALUE7, values[7]);
    mpz_set_ui(VALUE8, values[8]);

    // Calculate the squared values required for row 0 and 1
    mpz_mul(SQUARE0, VALUE0, VALUE0);
    mpz_mul(SQUARE1, VALUE1, VALUE1);
    mpz_mul(SQUARE2, VALUE2, VALUE2);
    mpz_mul(SQUARE3, VALUE3, VALUE3);
    mpz_mul(SQUARE4, VALUE4, VALUE4);
    mpz_mul(SQUARE5, VALUE5, VALUE5);

    // Calculate row 0
    mpz_add(ROW0, SQUARE0, SQUARE1);
    mpz_add(ROW0, ROW0, SQUARE2);

    // Calculate row 1
    mpz_add(ROW1, SQUARE3, SQUARE4);
    mpz_add(ROW1, ROW1, SQUARE5);

    // Check if row 1 equals row 0
    if (mpz_cmp(ROW1, ROW0) == 0) {

        // Calculate remaining squared values
        mpz_mul(SQUARE6, VALUE6, VALUE6);
        mpz_mul(SQUARE7, VALUE7, VALUE7);
        mpz_mul(SQUARE8, VALUE8, VALUE8);

        // Calculate row 2
        mpz_add(ROW2, SQUARE6, SQUARE7);
        mpz_add(ROW2, ROW2, SQUARE8);

        // Check if row 2 equals row 0
        if (mpz_cmp(ROW2, ROW0) == 0) {

            // Calculate column 0
            mpz_add(COLUMN0, SQUARE0, SQUARE3);
            mpz_add(COLUMN0, COLUMN0, SQUARE6);

            // Check if column 0 equals row 0
            if (mpz_cmp(COLUMN0, ROW0) == 0) {

                // Calculate column 1
                mpz_add(COLUMN1, SQUARE1, SQUARE4);
                mpz_add(COLUMN1, COLUMN1, SQUARE7);

                // Check if column 1 equals row 0
                if (mpz_cmp(COLUMN1, ROW0) == 0) {

                    // No need to calculate column 2
                    // If the sums of all rows and column 0 and 1 are equal, column 2 will be as well
                    // https://youtu.be/Kdsj84UdeYg?feature=shared&t=490

                    // Calculate diagonal 0
                    mpz_add(DIAGONAL0, SQUARE0, SQUARE4);
                    mpz_add(DIAGONAL0, DIAGONAL0, SQUARE8);

                    // Check if diagonal 0 equals row 0
                    if (mpz_cmp(DIAGONAL0, ROW0) == 0) {

                        // Calculate diagonal 1
                        mpz_add(DIAGONAL1, SQUARE2, SQUARE4);
                        mpz_add(DIAGONAL1, DIAGONAL1, SQUARE6);

                        // Check if diagonal 1 equals row 0
                        if (mpz_cmp(DIAGONAL1, ROW0) == 0) {

                            // A full magic square was found!!!

                            // Log magic square with type 0
                            logMagicSquare(0, values);

                        // A magic square with all rows, all columns and one diagonal was found
                        } else {

                            // Log magic square with type 1
                            logMagicSquare(1, values);

                        }

                    // A magic square with all rows, all columns and no diagonal was found
                    } else {

                        // Log magic square with type 2
                        logMagicSquare(2, values);

                    }
                
                // A magic square with all rows and one column was found
                } else {

                    // Log magic square with type 4
                    logMagicSquare(4, values);

                }

            }

        }

    }

}

// ================================================================================================
// Main function
// ================================================================================================
int main() {

    // Register interrupt signal handler
    signal(SIGINT, cleanup);

    // Register termination signal handler
    signal(SIGTERM, cleanup);

    // Initialize GMP integer variables
    mpz_inits(
        VALUE0,
        VALUE1,
        VALUE2,
        VALUE3,
        VALUE4,
        VALUE5,
        VALUE6,
        VALUE7,
        VALUE8,
        SQUARE0,
        SQUARE1,
        SQUARE2,
        SQUARE3,
        SQUARE4,
        SQUARE5,
        SQUARE6,
        SQUARE7,
        SQUARE8,
        ROW0,
        ROW1,
        ROW2,
        COLUMN0,
        COLUMN1,
        DIAGONAL0,
        DIAGONAL1,
        NULL
    );

    // Create a random device to seed the random number generator
    random_device randomDevice;

    // Initialize a Mersenne Twister engine with the random seed
    mt19937 generator(randomDevice());

    // Define a uniform distribution
    uniform_int_distribution<uint64_t> distribution(SEARCH_RANGE_MINIMUM, SEARCH_RANGE_MAXIMUM);

    // Loop forever
    while (true) {

        // Record batch start time
        auto start = chrono::high_resolution_clock::now();

        for (uint64_t batch = 0; batch < BATCH_SIZE; batch++) {

            // Create an array of 9 values
            uint64_t values[9] = {};

            // Get 9 unique random values
            getValues(distribution, generator, values);

            // Calculate a magic square
            calculateMagicSquare(values);

        }

        // Record batch end time
        auto end = chrono::high_resolution_clock::now();

        // Compute duration in milliseconds
        chrono::duration<double, milli> duration = end - start;

        // Print JSON status message
        cout << "{\"message\":\"status\",\"minimum\":" << SEARCH_RANGE_MINIMUM << ",\"maximum\":" << SEARCH_RANGE_MAXIMUM << ",\"iterations\":" << BATCH_SIZE << ",\"durationMilliseconds\":" << static_cast<uint64_t>(duration.count()) << "}" << endl;

    }

    // If the loop breaks, clean up
    cleanup(0);

    // Exit
    return 0;

}