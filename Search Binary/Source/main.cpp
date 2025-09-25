#include <cstdint>
#include <string>
#include <vector>
#include <utility>
#include <cmath>
#include <set>
#include <stdexcept>
#include <gmpxx.h>
#include <iostream>

using namespace std;

// Magic square struct
struct MagicSquare {

    uint64_t a;
    uint64_t b;
    uint64_t c;
    uint64_t d;
    uint64_t e;
    uint64_t f;
    uint64_t g;
    uint64_t h;
    uint64_t i;

};

// ================================================================================================
// Get all valid (1 mod 4) prime factors for 2E²
// ================================================================================================
vector<pair<uint64_t, uint64_t>> getValidPrimeFactors(uint64_t e) {

    // List of valid prime factors and their exponent as a pair of integers
    vector<pair<uint64_t, uint64_t>> primeFactors;

    // Only odd numbers should be passed to this function
    // So no need to check for a prime factor of 2

    // For every odd factor up to the square root of E
    for (uint64_t factor = 3; factor <= e / factor; factor += 2) {

        // If the factor divides E, then the factor is a prime
        if (e % factor == 0) {

            // If the prime factor is not congruent 1 mod 4, return no valid prime factors
            if (factor % 4 != 1) { return {}; }

            // Exponent of the prime factor
            uint64_t exponent = 0;

            // Loop until E is no longer divisible by the prime factor
            while (e % factor == 0) {

                // Increase the exponent of the factor
                // The exponent is increased in steps of 2 to make it a valid prime factor for 2E²
                exponent += 2;

                // Divide out the prime factor from E
                e /= factor;

            }

            // Add the prime factor and its exponent to the list of prime factors
            primeFactors.emplace_back(factor, exponent);

        }

    }

    // If after the loop E is still larger that 1, then the remaining E is a prime
    if (e > 1) {

        // If the remaining prime factor is not congruent 1 mod 4, return no valid prime factors
        if (e % 4 != 1) { return {}; }

        // Add the remaining E as a prime factor with an exponent of 2 to the list of valid prime factors
        // The exponent is 2 to make it a valid prime factor of 2E²
        primeFactors.emplace_back(e, 2);


    }

    // Return the list of valid prime factors
    return primeFactors;

}

// ================================================================================================
// Use the sum of two squares theorem to count the number of unique ways 2E² could be represented as a sum of two squares
// ================================================================================================
uint64_t countUniqueSumOfSquares(const vector<pair<uint64_t, uint64_t>>& primeFactors) {

    // Number of solutions to the sum of two squares theorem
    uint64_t count = 4;

    // For each prime factor and its exponent
    for (auto& [prime, exponent] : primeFactors) {

        // All prime factors of 2E² are proven to be congruent to 1 mod 4
        // No need to check additional constraints of the sum of two squares theorem

        // Update the number of solutions to the sum of two squares theorem
        count *= exponent + 1;

    }

    // Compensate for unique ordering and negative solutions
    count /= 8;

    // Return the number of solutions
    return count;

}

// Direct pair search method
#if DIRECT_PAIR_SEARCH

// ================================================================================================
// Direct (brut force) way of searching for all unique pairs of integers that if squared and summed would represent 2E²
// ================================================================================================
vector<pair<uint64_t, uint64_t>> getOrderedUniqueBasePairsDirect(const uint64_t e) {

    // This search function will only work to a value of E < 3037000499 or E < √(2⁶⁴÷2)
    // Because otherwise 2E² would overflow the maximum value of an unsigned 64 bit integer

    // Search constraints
    // 2E² = X² + Y²
    // X² ≠ Y²
    // X² > 0
    // X² < E²
    // Y² > E²
    // Y² < 2E²

    // List of base pairs
    vector<pair<uint64_t, uint64_t>> basePairs;

    // Target sum is 2E²
    uint64_t targetSum = 2 * e * e;

    // Y² > E² therfore Y > E and Y² < 2E² therfore Y < √2E²
    // Loop through every possible value of Y in decreasing order
    // Doing it in this way will automaticaly sort the pairs from smallest to largest
    for (uint64_t y = sqrt(targetSum); y > e; y--) {

        // Solve for X²
        uint64_t xSquared = targetSum - y * y;

        // Take the root of X² to get X 
        uint64_t x = sqrt(xSquared);

        // Check if X is a perfect square
        if (x * x == xSquared) {

            // Add to the list of base pairs
            basePairs.emplace_back(x, y);

        }

    }

    // Return the list of base pairs
    return basePairs;

}

// Brahmagupta-Fibonacci identity method
#else

// ================================================================================================
// Direct (brut force) way of getting a pair of integers that if squared and summed would represent a prime
// ================================================================================================
pair<uint64_t, uint64_t> getPrimeBasePairDirect(const uint64_t prime) {

    // For every possible base value as X up to the square root of the prime
    for (uint64_t x = 1; x <= prime / x; x++) {

        // Solve for Y²
        uint64_t ySquared = prime - x * x;

        // Take the root of Y² to get Y
        uint64_t y = sqrt(ySquared);

        // If Y is a perfect square
        if (y * y == ySquared) {

            // Return the base pair
            return {x, y};

        }

    }

    // Keep the compiler happy :)
    throw runtime_error("Prime can not be represented as a sum of two squares!");

}

// ================================================================================================
// Use the Brahmagupta-Fibonacci identity to get 2 sets of base pairs
// ================================================================================================
set<pair<uint64_t, uint64_t>> getBrahmaguptaFibonacciIdentityPairs(const pair<uint64_t, uint64_t>& pair1, const pair<uint64_t, uint64_t>& pair2) {

    // Multiply values
    uint64_t product1 = pair1.first  * pair2.first;
    uint64_t product2 = pair1.second * pair2.second;
    uint64_t product3 = pair1.first  * pair2.second;
    uint64_t product4 = pair1.second * pair2.first;

    // Calculate absolute values, ensure no negative solutions
    uint64_t x1 = product1 > product2 ? product1 - product2 : product2 - product1;
    uint64_t y1 = product3 + product4;
    uint64_t x2 = product1 + product2;
    uint64_t y2 = product3 > product4 ? product3 - product4 : product4 - product3;

    // Ensure unique ordering and therefore no duplicates
    if (x1 > y1) { swap(x1, y1); }
    if (x2 > y2) { swap(x2, y2); }

    // Return all unique pairs
    return {

        {x1, y1},
        {x2, y2}

    };

}

// ================================================================================================
// Get all unique pairs of of integers that if squared and summed would represent a prime factor
// ================================================================================================
set<pair<uint64_t, uint64_t>> getUniquePrimeFactorBasePairs(const pair<uint64_t, uint64_t>& primeFactor) {

    // Get a pair of integers that if squared and summed would represent the prime factor in its base form
    pair<uint64_t, uint64_t> primeBasePair = getPrimeBasePairDirect(primeFactor.first);

    // Set of unique integer pairs that if squared and summed would represent the prime factor in its raised form
    // Initialized with the pair of integers of the prime in its base form P¹
    set<pair<uint64_t, uint64_t>> basePairs = {primeBasePair};

    // Loop for the number of times the prime is raised to it exponent starting from P¹
    for (uint64_t exponent = 1; exponent < primeFactor.second; exponent++) {

        // New temporary set of base pairs
        set<pair<uint64_t, uint64_t>> newBasePairs;

        // For every base pair in the set of all unique base pairs
        for (auto& basePair : basePairs) {

            // Get a new set of base pairs using the Brahmagupta–Fibonacci identity and add it to the new base pairs set
            newBasePairs.merge(getBrahmaguptaFibonacciIdentityPairs(basePair, primeBasePair));

        }

        // Set the base pair set to the new base pair set
        basePairs = newBasePairs;

    }

    // Return the set of base pairs
    return basePairs;

}

// ================================================================================================
// Get all unique pairs of of integers that if squared and summed would represent 2E²
// ================================================================================================
vector<pair<uint64_t, uint64_t>> getOrderedUniqueBasePairs(const vector<pair<uint64_t, uint64_t>>& primeFactors) {

    // Set of unique integer pairs that if squared and summed would represent 2E²
    set<pair<uint64_t, uint64_t>> basePairs = {{1, 0}};

    // For every prime factor of 2E²
    for (auto& primeFactor : primeFactors) {

        // Get a set of unique pairs of integers that if squared and summed would represent the prime factor of 2E²
        set<pair<uint64_t, uint64_t>> primeBasePairs = getUniquePrimeFactorBasePairs(primeFactor);

        // New temporary set of base pairs
        set<pair<uint64_t, uint64_t>> newBasePairs;

        // For every base pair in the set of all unique base pairs
        for (auto& basePair : basePairs) {

            // For every prime factor base pair in the set of all unique prime factor base pairs
            for (auto& primeBasePair : primeBasePairs) {

                // Get a new set of base pairs using the Brahmagupta–Fibonacci identity and add it to the new base pairs set
                newBasePairs.merge(getBrahmaguptaFibonacciIdentityPairs(basePair, primeBasePair));

            }

        }

        // Set the base pair set to the new base pair set
        basePairs = newBasePairs;

    }

    // Create a new list of ordered and unique base pairs
    vector<pair<uint64_t, uint64_t>> orderedUniqueBasePairs;

    // For every base pair
    for (auto& basePair : basePairs) {

        // Check if both values are not the same
        // To ensure 2E² = X² + Y² where X² != Y²
        if (basePair.first != basePair.second) {

            // Add the unique valid pair to the list
            orderedUniqueBasePairs.push_back(basePair);

        }

    }

    // Retrun the sorted list
    return orderedUniqueBasePairs;

}

// End of search method selection
#endif

// ================================================================================================
// Test a magic square candidate (precision limited, but fast)
// ================================================================================================
void testMagicSquareLimited(const MagicSquare& magicSquare) {

    // Square values
    // Works for a value of E < 3037000499 or E < √(2⁶⁴÷2)
    // Because H² could be almost as large as 2E² and with E being more than 3,037,000,499 that would overflow a 64 bit integer
    uint64_t aSquared = magicSquare.a * magicSquare.a;
    uint64_t bSquared = magicSquare.b * magicSquare.b;
    uint64_t cSquared = magicSquare.c * magicSquare.c;
    uint64_t gSquared = magicSquare.g * magicSquare.g;
    uint64_t hSquared = magicSquare.h * magicSquare.h;
    uint64_t iSquared = magicSquare.i * magicSquare.i;

    // Calculate top and bottom row sums
    // Works for a value of E < 1920767766 or √(2⁶⁴÷5)
    // Because the sum of A² + B² + C² could be almost 5E² and with E being more than 1,920,767,766 that would overflow a 64 bit integer
    uint64_t row1Sum = aSquared + bSquared + cSquared;
    uint64_t row3Sum = gSquared + hSquared + iSquared;

    // Check if top and bottom row are identical
    // This is a requirement of a working magic square
    if (row1Sum == row3Sum) {

        // Square remaining values
        uint64_t dSquared = magicSquare.d * magicSquare.d;
        uint64_t eSquared = magicSquare.e * magicSquare.e;
        uint64_t fSquared = magicSquare.f * magicSquare.f;

        // Print result as JSON
        cout << "{\"e\": " << magicSquare.e << ", \"aSquared\": " << aSquared << ", \"bSquared\": " << bSquared << ", \"cSquared\": " << cSquared << ", \"dSquared\": " << dSquared << ", \"eSquared\": " << eSquared << ", \"fSquared\": " << fSquared << ", \"gSquared\": " << gSquared << ", \"hSquared\": " << hSquared << ", \"iSquared\": " << iSquared << "}" << endl;

    }

}

// ================================================================================================
// Test a magic square candidate (arbitrary precision, but slow)
// ================================================================================================
void testMagicSquare(const MagicSquare& magicSquare) {

    // Static GMP integers
    static mpz_class aSquared, bSquared, cSquared, dSquared, eSquared, fSquared, gSquared, hSquared, iSquared, row1Sum, row3Sum;

    // Convert uint64_t values to GMP integer
    aSquared = magicSquare.a;
    bSquared = magicSquare.b;
    cSquared = magicSquare.c;
    gSquared = magicSquare.g;
    hSquared = magicSquare.h;
    iSquared = magicSquare.i;

    // Square values
    aSquared = aSquared * aSquared;
    bSquared = bSquared * bSquared;
    cSquared = cSquared * cSquared;
    gSquared = gSquared * gSquared;
    hSquared = hSquared * hSquared;
    iSquared = iSquared * iSquared;

    // Calculate top and bottom row sums
    row1Sum = aSquared + bSquared + cSquared;
    row3Sum = gSquared + hSquared + iSquared;

    // Check if top and bottom row are identical
    // This is a requirement of a working magic square
    if (row1Sum == row3Sum) {

        // Convert remaining values to GMP integer
        dSquared = magicSquare.d;
        eSquared = magicSquare.e;
        fSquared = magicSquare.f;

        // Square remaining values
        dSquared = dSquared * dSquared;
        eSquared = eSquared * eSquared;
        fSquared = fSquared * fSquared;

        // Print result as JSON
        cout << "{\"e\": " << magicSquare.e << ", \"aSquared\": " << aSquared << ", \"bSquared\": " << bSquared << ", \"cSquared\": " << cSquared << ", \"dSquared\": " << dSquared << ", \"eSquared\": " << eSquared << ", \"fSquared\": " << fSquared << ", \"gSquared\": " << gSquared << ", \"hSquared\": " << hSquared << ", \"iSquared\": " << iSquared << "}" << endl;

    }

}

// ================================================================================================
// Main
// ================================================================================================
int main(int, char* launchArguments[]) {

    // Get the start and end index of the search range
    uint64_t startIndex = stoull(launchArguments[1]);
    uint64_t endIndex   = stoull(launchArguments[2]);

    // If the start index is an even number decrease it by one to make it odd
    if (startIndex % 2 == 0) { startIndex--; }

    // For every odd number as E in the search range
    for (uint64_t e = startIndex; e < endIndex; e += 2) {

        // Check if E is congruent to 1 mod 4
        // This is a requirement (but not a guarantee) for all prime factors of 2E² to also be congruent to 1 mod 4
        if (e % 4 == 1) {

            // Get all valid (1 mod 4) prime factors for 2E²
            vector<pair<uint64_t, uint64_t>> primeFactors = getValidPrimeFactors(e);

            // Check if there are any valid prime factors for 2E²
            if (!primeFactors.empty()) {

                // Get the number of unique ways to represented 2E² as a sum of two squares
                uint64_t totalUniqueSumOfSquares = countUniqueSumOfSquares(primeFactors);

                // Check if there are at least 4 unique ways to represented 2E² as a sum of two squares
                if(totalUniqueSumOfSquares >= 4) {

                    // Manually add 2¹ as a valid prime factor for 2E²
                    primeFactors.emplace_back(2, 1);

                    // Use the direct pair search method
                    #if DIRECT_PAIR_SEARCH

                        // Get all pairs of integers that if squared and summed would represent 2E²
                        vector<pair<uint64_t, uint64_t>> basePairs = getOrderedUniqueBasePairsDirect(e);

                    // Use the Brahmagupta-Fibonacci identity method
                    #else

                        // Get all pairs of integers that if squared and summed would represent 2E²
                        vector<pair<uint64_t, uint64_t>> basePairs = getOrderedUniqueBasePairs(primeFactors);

                    #endif

                    // If calculated and actual number of pairs of integers that if squared and summed would represent 2E² dont match
                    if (totalUniqueSumOfSquares != basePairs.size()) {

                        // Throw a runtime error because something has gone wrong
                        throw runtime_error("Calculated and actual number of ways to represent 2E² don't match!");

                    }

                    // Iterate through all possible pair positions of the magic square
                    // Excluding rotations and mirrors by fixing the pairs in specific positions based on the pair size
                    // This is to limit the number of combinations that need to be tested
                    for (uint64_t column2 = 0; column2 < basePairs.size(); column2++) {
                        for (uint64_t diagonal1 = column2 + 1; diagonal1 < basePairs.size(); diagonal1++) {
                            for (uint64_t row2 = diagonal1 + 1; row2 < basePairs.size(); row2++) {
                                for (uint64_t diagonal2 = row2 + 1; diagonal2 < basePairs.size(); diagonal2++) {

                                    // Construct a magic square candidate with the base value pairs in their fixed positions
                                    MagicSquare magicSquare = {

                                        /* A */ basePairs[diagonal1].second,
                                        /* B */ basePairs[column2].first,
                                        /* C */ basePairs[diagonal2].second,
                                        /* D */ basePairs[row2].first,
                                        /* E */ e,
                                        /* F */ basePairs[row2].second,
                                        /* G */ basePairs[diagonal2].first,
                                        /* H */ basePairs[column2].second,
                                        /* I */ basePairs[diagonal1].first

                                    };

                                    // If E < 1.7*10⁹ use the fast precision limited approach
                                    // 1.7*10⁹ is around 90% of √(2⁶⁴÷5) with is the maximum value of E the precision limited test can handle
                                    // There is a 10% safety margin in the calculation to prevent race conditions
                                    if (e < 1700000000) {

                                        // Test the magic square candidate and print any valid results
                                        testMagicSquareLimited(magicSquare);
                                    
                                    // If E > 1.7*10⁹ use the slow arbitrary precision approach
                                    } else {

                                        // Test the magic square candidate and print any valid results
                                        testMagicSquare(magicSquare);

                                    }

                                }
                            }
                        }
                    }

                }

            }

        }

    }

    // Exit
    return 0;

}