/* 

    A "less" naive approach for finding a 3x3 magic square of squares.

    This program generates a set of 3 unique random weights.
    Those weights are used to generate a set of values for a working magic square (https://en.wikipedia.org/wiki/Magic_square).
    Those values are then checked to determine if their square root is an integer, indicating that they are perfect squares.
    This is repeated forever, regularly printing status messages.

    For the main calculations, the GMP library is used.
    This library provides integers with arbitrary precision / length.

    Lower and upper bounds for the search range, i.e., the minimum and maximum weight values, can be set with SEARCH_RANGE_MINIMUM and SEARCH_RANGE_MAXIMUM.
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

// Minimum value a weight can be
const int64_t SEARCH_RANGE_MINIMUM = -5000;

// Maximum value a weight can be
const uint64_t SEARCH_RANGE_MAXIMUM = 10000;

// Number of iterations that will be performed in each loop 
const uint64_t BATCH_SIZE = 1000000000;

// Type of magic square the result has to be before it gets logged
// A perfect square is 0, a less perfect square is 1, and so on
const uint8_t LOG_SQUARE_TYPE = 10;

// GMP integers
mpz_t
    X,
    Y,
    Z,
    VALUE0,
    VALUE1,
    VALUE2,
    VALUE3,
    VALUE4,
    VALUE5,
    VALUE6,
    VALUE7
;

// ================================================================================================
// Cleanup function
// ================================================================================================
void cleanup(int signal) {

    // Clear up the allocated memory
    mpz_clears(
        X,
        Y,
        Z,
        VALUE0,
        VALUE1,
        VALUE2,
        VALUE3,
        VALUE4,
        VALUE5,
        VALUE6,
        VALUE7,
        NULL
    );

    // Exit
    exit(signal);

}

// ================================================================================================
// Get a set of 3 unique random weights
// ================================================================================================
void getWeights(uniform_int_distribution<int64_t> &distribution, mt19937 &generator, int64_t *weights) {

    // Number of unique weights
    uint8_t unique = 0;

    // Loop unil 3 unique weights are generated
    while (unique < 3) {

        // Get a random number in the search range
        int64_t number = distribution(generator);

        // Variable for checking if the array already contains the weight
        bool contains = false;

        // For all elements in the array of weights
        for (uint8_t weight = 0; weight < 3; weight++) {

            // If the weight is already in the array
            if (weights[weight] == number) {

                // Set the contains flag to true
                contains = true;

                // Break the loop immediately
                break;

            }

        }

        // If the array doesn't contain the weight, i.e., it's unique
        if (!contains) {

            // Add the unique weight to the array
            weights[unique] = number;

            // Increase the number of unique weights
            unique++;

        }

    }

    // Always use a positive value for weight 0
    weights[0] = abs(weights[0]);

}

// ================================================================================================
// Log weights
// ================================================================================================
void logWeights(uint16_t type, int64_t *weights) {

    // Only log result if magic square is of certain type
    if (type <= LOG_SQUARE_TYPE) {

        // Print the result as JSON
        cout << "{\"message\":\"weights\",\"type\":" << type << ",\"weights\":[";

        // For each weight
        for (uint8_t weight = 0; weight < 3; weight++) {

            // Add the weight to the JSON array
            cout << weights[weight];

            // If not the last weight add a ","
            if (weight + 1 < 3) {

                cout << ",";

            }

        }

        // Add trailing "]}"
        cout << "]}" << endl;

    }

}

// ================================================================================================
// Calculate working magic square and check if the square root is an integer
// ================================================================================================
void calculateMagicSquare(int64_t *weights) {

    // Convert int64_t values to values with arbitrary precision
    mpz_set_si(X, weights[0]);
    mpz_set_si(Y, weights[1]);
    mpz_set_si(Z, weights[2]);

    // Check if the main weight (the center value) is a perfect square
    if (mpz_perfect_square_p(X)) {

        // Calculate value 0 (x - y)
        mpz_sub(VALUE0, X, Y);

        // Check if value 0 is positive and a perfect square
        if (mpz_sgn(VALUE0) >= 0 && mpz_perfect_square_p(VALUE0)) {

            // Calculate value 1 (x + y + z)
            mpz_add(VALUE1, X, Y); 
            mpz_add(VALUE1, VALUE1, Z);

            // Check if value 1 is positive and a perfect square
            if (mpz_sgn(VALUE1) >= 0 && mpz_perfect_square_p(VALUE1)) {

                // Calculate value 2 (x - z)
                mpz_sub(VALUE2, X, Z);

                // Check if value 2 is positive and a perfect square
                if (mpz_sgn(VALUE2) >= 0 && mpz_perfect_square_p(VALUE2)) {

                    // Calculate value 3 (x + y - z)
                    mpz_add(VALUE3, X, Y);
                    mpz_sub(VALUE3, VALUE3, Z);

                    // Check if value 3 is positive and a perfect square
                    if (mpz_sgn(VALUE3) >= 0 && mpz_perfect_square_p(VALUE3)) {

                        // Calculate value 4 (x - y + z)
                        mpz_sub(VALUE4, X, Y);
                        mpz_add(VALUE4, VALUE4, Z);

                        // Check if value 4 is positive and a perfect square
                        if (mpz_sgn(VALUE4) >= 0 && mpz_perfect_square_p(VALUE4)) {

                            // Calculate value 5 (x + z)
                            mpz_add(VALUE5, X, Z);

                            // Check if value 5 is positive and a perfect square
                            if (mpz_sgn(VALUE5) >= 0 && mpz_perfect_square_p(VALUE5)) {

                                // Calculate value 6 (x - y - z)
                                mpz_sub(VALUE6, X, Y);
                                mpz_sub(VALUE6, VALUE6, Z);

                                // Check if value 6 is positive and a perfect square
                                if (mpz_sgn(VALUE6) >= 0 && mpz_perfect_square_p(VALUE6)) {

                                    // Calculate value 7 (x + y)
                                    mpz_add(VALUE7, X, Y);

                                    // Check if value 7 is positive and a perfect square
                                    if (mpz_sgn(VALUE7) >= 0 && mpz_perfect_square_p(VALUE7)) {

                                        // A full magic square was found!!!

                                        // Log weights that result in that square
                                        logWeights(0, weights);

                                    // Weight that will result in an almost perfect square
                                    } else {

                                        // Log weights that result in that square
                                        logWeights(2, weights);

                                    }
                                
                                // Weight that will result in not perfect square
                                } else {

                                    // Log weights that result in that square
                                    logWeights(3, weights);

                                }
                            
                            // Weight that will result in not perfect square
                            } else {

                                // Log weights that result in that square
                                logWeights(4, weights);

                            }
                        
                        // Weight that will result in not perfect square
                        } else {

                            // Log weights that result in that square
                            logWeights(5, weights);

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
int main() {

    // Register interrupt signal handler
    signal(SIGINT, cleanup);

    // Register termination signal handler
    signal(SIGTERM, cleanup);

    // Initialize GMP integer variables
    mpz_inits(
        X,
        Y,
        Z,
        VALUE0,
        VALUE1,
        VALUE2,
        VALUE3,
        VALUE4,
        VALUE5,
        VALUE6,
        VALUE7,
        NULL
    );

    // Create a random device to seed the random number generator
    random_device randomDevice;

    // Initialize a Mersenne Twister engine with the random seed
    mt19937 generator(randomDevice());

    // Define a uniform distribution
    uniform_int_distribution<int64_t> distribution(SEARCH_RANGE_MINIMUM, SEARCH_RANGE_MAXIMUM);

    while (true) {

        // Record batch start time
        auto start = chrono::high_resolution_clock::now();

        for (uint64_t batch = 0; batch < BATCH_SIZE; batch++) {

            // Array of weight
            int64_t weights[3] = {};

            // Get 3 unique random weights
            getWeights(distribution, generator, weights);

            // Calculate a magic square
            calculateMagicSquare(weights);

        }

        // Record batch end time
        auto end = chrono::high_resolution_clock::now();

        // Compute duration in milliseconds
        chrono::duration<double, milli> duration = end - start;

        // Print JSON status message
        cout << "{\"message\":\"status\",\"minimum\":" << SEARCH_RANGE_MINIMUM
        << ",\"maximum\":" << SEARCH_RANGE_MAXIMUM
        << ",\"iterations\":" << BATCH_SIZE
        << ",\"durationMilliseconds\":" << static_cast<uint64_t>(duration.count()) 
        << "}" << endl;

    }

    // If the loop breaks, clean up
    cleanup(0);

    // Exit
    return 0;
    
}