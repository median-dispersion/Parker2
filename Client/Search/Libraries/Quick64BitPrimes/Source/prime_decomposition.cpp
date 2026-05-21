#include "Quick64BitPrimes/prime_decomposition.hpp"
#include "Quick64BitPrimes/types.hpp"
#include "Quick64BitPrimes/modular_arithmetic.hpp"
#include "Quick64BitPrimes/miller_rabin_primality_test.hpp"
#include <vector>
#include <random>
#include <numeric>
#include <algorithm>

namespace q64bp {

    // ============================================================================================
    // Prime decomposition using trial division but only for factors in the form factor ≡ 1 (mod 4)
    // ============================================================================================
    bool trial_division_1mod4_unsafe(
        ui64 number,
        std::vector<ui64>& primes
    ) {

        // This function must be called through squared_prime_decomposition_1mod4()!
        // Otherwise it is unsafe to use!
        // This function will get all prime factors of the number
        // But only if every prime factor is in the form factor ≡ 1 (mod 4)
        // If it isn't it will return false

        // Loop through every odd factor up to the square root of the number
        for(ui64 factor = 3; factor * factor <= number; factor += 2) {

            // Check if the number is divisible by the factor
            if (number % factor == 0) {

                // If the prime factor is not in the form factor ≡ 1 (mod 4) return no valid prime factors
                if ((factor & 3) != 1) { return false; }

                // Loop as long as the number is divisible by the factor
                while (number % factor == 0) {

                    // Divide out the prime factor
                    number /= factor;

                    // Add the prime factor to the list of primes
                    primes.push_back(factor);

                }

            }

        }

        // If the number is still more than one, it is a prime
        if (number > 1) {

            // If the prime factor is not in the form factor ≡ 1 (mod 4) return no valid prime factors
            if ((number & 3) != 1) { return false; }

            // Add the prime factor to the list of primes
            primes.push_back(number);

        }

        // Return that all prime factors where valid
        return true;

    }

    // ============================================================================================
    // Modular polynomial f(x) = (x² + c) mod m for advancing the position in Pollard's rho algorithm
    // ============================================================================================
    ui64 advance_position(
        ui64 variable,
        ui64 constant,
        ui64 modulus
    ) {
        return modular_addition(modular_multiplication(variable, variable, modulus), constant, modulus);
    }

    // ============================================================================================
    // Integer factorization using Pollard's rho algorithm and Brent's cycle detection method
    // https://en.wikipedia.org/wiki/Pollard%27s_rho_algorithm#Algorithm
    // ============================================================================================
    ui64 pollard_brent_factorization_unsafe(ui64 number) {

        // This function must be called through squared_prime_decomposition_1mod4()!
        // Otherwise it is unsafe to use!

        // Initialize the random number generator
        static std::mt19937_64 rng(std::random_device{}());

        // Get a uniform distribution to choose a random constant for the polynomial function
        // The range is 1 to number - 1
        // Defined as 1 to number - 2, because number - 2 will later be skipped by adding one
        std::uniform_int_distribution<ui64> anchor(1, number - 2);

        // Get a uniform distribution to choose a random start postion for the tortoise, hare and fox
        // The range is 2 to number - 2
        // This is to avoid trivial or degenerate cases
        std::uniform_int_distribution<ui64> position(2, number - 2);

        // Define the maximum number of steps the hare can do in one sprint
        // This is Brent's tuning factor "m"
        // A value of 128 seems like a good value for all input ranges
        ui64 sprint_length = 128;

        // Limit the number of attempts to find a non trivial factor
        // Pollard's Rho "should" find a non trivial factor
        // Especially when retrying with randomized parameters for the polynomial function
        // But there seems to be no proof that if all possible combination of parameters are exhausted that a non trivial factor will be found
        // This is why the number of attempts is limited and if no factor is found an invalid solution of 0 is returned
        // During testing the maximum number of attempts reached was 32
        // This multiplied with a safety factor of 8
        // So for 99.999..% of the time the algorithm will return a valid solution
        // And for the astronomically small chance that it fails it limits the number of attempts instead of hanging forever
        for (ui64 attempt = 0; attempt < 256; attempt++) {

            // Initialize the factor as one
            ui64 factor = 1;

            // Initialize the start positions of the hare, tortoise and fox
            // Randomize the start position for each attempt
            ui64 hare = position(rng);
            ui64 tortoise = hare;
            ui64 fox = hare;

            // Initialize the constant of the polynomial function
            // Randomize the constant for each attempt
            ui64 constant = anchor(rng);

            // Skip constant = number - 2, by adding one to the constant
            if (constant == number - 2) { constant++; }

            // Repeatedly perform races between the tortoise and the hare
            // Doubling the race length each time
            // Do this until the maximum race length has been reached or a factor has been found
            // During testing the maximum length the race reached was 262'144
            // This multiplied with a safety factor of 8
            for (ui64 race_length = 1; race_length < 2'097'152 && factor == 1; race_length <<= 1) {

                // The tortoise and hare start on the same position
                tortoise = hare;

                // Let the hare take as many steps as the race is long (cheater!)
                for (ui64 step = 0; step < race_length; step++) {

                    // Advance the position of the hare
                    hare = advance_position(hare, constant, number);

                }

                // Initialize the accumulative distance between the tortoise and the hare
                // This will be updated after each sprint of the hare
                ui64 distance = 1;

                // Let the hare perform a short sprint
                // Do as many sprints as fit in the race or until a factor is found
                for (ui64 sprint = 0; sprint < race_length && factor == 1; sprint += sprint_length) {

                    // Before each sprint, the fox and hare meat up
                    // The fox stays at this position, keeping a lookout for the tortoise
                    fox = hare;

                    // Let the hare take as steps many as the sprint is long
                    // Or as many steps as are remaining in the race
                    for (ui64 step = 0; step < sprint_length && step < race_length - sprint; step++) {

                        // Advance the position of the hare
                        hare = advance_position(hare, constant, number);

                        // Update the accumulative distance between the tortoise and hare
                        distance = modular_multiplication(
                            distance,
                            tortoise < hare ? hare - tortoise : tortoise - hare,
                            number
                        );

                    }

                    // After each sprint try to find a hidden factor in the accumulate distance
                    factor = std::gcd(distance, number);

                }

            }

            // After all the races are completed, check if the factor is the number itself
            // This means the hare overshot the goal of the race
            if (factor == number) {

                // Reset the factor to try and find a non trivial one
                factor = 1;

                // The fox is a good sport and performs one final race between him and the tortoise
                // He takes as many steps as this final race is long, or until a factor has been found
                // During testing the maximum length of the final race reached was 128
                // This multiplied with a safety factor of 8
                for (ui64 step = 0; step < 1024 && factor == 1; step++) {

                    // Advance the position of the fox
                    // The fox is only doing on step at a time instead of sprinting like tha hare did
                    fox = advance_position(fox, constant, number);

                    // After each step try to find a hidden factor in the distance between the tortoise and fox
                    factor = std::gcd(
                        tortoise < fox ? fox - tortoise : tortoise - fox,
                        number
                    );

                }

            }

            // If a non trivial factor was found return it
            if (factor > 1 && factor < number) { return factor; }

            // If no non trivial factor was found
            // Retry with new randomized start positions and parameters for the polynomial function

        }

        // If the maximum number of attempts was reached (extremely unlikely)
        // No non trivial factor was found
        // Return an invalid solution
        return 0;

    }

    // ============================================================================================
    // Decompose a number into its prime factors
    // ============================================================================================
    std::vector<PrimeFactor> squared_prime_decomposition_1mod4(ui64 number) {

        // Any number passed to this function must be:
        // number >= 5
        // number == odd
        // number ≡ 1 (mod 4)
        // number != prime
        // Otherwise it is unsafe to use!

        // This function will get all prime factors of the number
        // But only if every prime factor is in the form factor ≡ 1 (mod 4)
        // Every prime factor exponent will be double of what it should be
        // This is because it treats the input number as squared
        // So the returned prime factors will be for number²

        // Initialize a list for all factors and all primes
        std::vector<ui64> factors;
        std::vector<ui64> primes;

        // Reserve size for 64 entries
        // An unsigned 64-bit integer can only have 64 factors
        // 2⁶⁴ = 2 x 2 x 2 ... 64 times
        factors.reserve(64);
        primes.reserve(64);

        // Add the number to the list of factors
        factors.push_back(number);

        // Loop until there are no more factors
        while (!factors.empty()) {

            // Get the latest factor from the list of all factors
            ui64 factor = factors.back();

            // Remove the latest factor from the list of all factors
            factors.pop_back();

            // Check if the latest factor is a prime
            if (miller_rabin_primality_test(factor)) {

                // If the prime factor is not in the form factor ≡ 1 (mod 4) return no valid prime factors
                if ((factor & 3) != 1) { return {}; }

                // Add the latest factor to the list of primes
                primes.push_back(factor);

                // Continue with the next factor
                continue;

            }

            // Check if the factor is less than 30'000'000
            if (factor < 30'000'000) {

                // Use trial division to break down the number into prime factors
                // Trial division is generally faster for small numbers up to around 30 million
                // The trial division will return false if it finds any factor that is not in the form factor ≡ 1 (mod 4)
                // In that case return no valid prime factors
                if (!trial_division_1mod4_unsafe(factor, primes)) { return {}; }

                // Continue with the next factor
                continue;

            }

            // Break down the latest factor into a new factor using Pollard's rho
            ui64 new_factor_1 = pollard_brent_factorization_unsafe(factor);

            // Check if a valid new factor was found
            if (new_factor_1) {

                // Deduce the other new factor
                ui64 new_factor_2 = factor / new_factor_1;

                // Add the two new factors to the list of all factors
                factors.push_back(new_factor_1);
                factors.push_back(new_factor_2);

            // If Pollard's rho failed to find a non trivial factor
            } else {

                // Use a deterministic approach like trial division
                // This is significantly slower especially for large factors
                // But in practice this should never happen and is just a fallback
                // The trial division will return false if it finds any factor that is not in the form factor ≡ 1 (mod 4)
                // In that case return no valid prime factors
                if (!trial_division_1mod4_unsafe(factor, primes)) { return {}; }

            }

        }

        // Sort the list of primes from smallest to largest
        std::sort(primes.begin(), primes.end());

        // Initialize a list of all prime factors
        std::vector<PrimeFactor> prime_factors;

        // Reserve space for 15 prime factors
        // An unsigned 64-bit integer can only have 15 prime factors
        // Because the first 16 primes multiplied together would overflow the 64-bit range
        prime_factors.reserve(15);

        // Loop through the list of sorted primes
        for (ui64 index = 0; index < primes.size();) {

            // Initialize the prime factor base and exponent
            ui64 base = primes[index];
            ui64 exponent = 0;

            // Check if the next prime is the same as the current prime
            while (base == primes[index] && index < primes.size()) {

                // Increase the exponent by two
                // This is because at this point the number is treated as if it is squared
                // Any prime factor exponent of a squared number is twice that of the unsquared number
                exponent += 2;

                // Continue with the next prime in the list
                index++;

            }

            // Add the prime factor to the list of prime factors
            prime_factors.emplace_back(base, exponent);

        }

        // Return the list of prime factors
        return prime_factors;

    }

}