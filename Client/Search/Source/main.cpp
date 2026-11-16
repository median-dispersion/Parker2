#include "types.hpp"
#include <string>

// ================================================================================================
// Main
// ================================================================================================
int main(int, char *argv[]) {

    // Get the start and end index of the search range
    // Maximum value for e = 2⁶⁴-1
    ui64 start_index = std::stoull(argv[1]);
    ui64 end_index = std::stoull(argv[2]);

    // Make sure the start index is at least 5
    if (start_index < 5) { start_index = 5; }

    // Make sure the start index is in the form start_index ≡ 1 (mod 4)
    // If it is not increase the start index to the next value that is in the form 1 (mod 4)
    // Maximum value for e = 2⁶⁴-4
    start_index += (1 - start_index % 4 + 4) % 4;

    // Loop through every value in the search range where e ≡ 1 (mod 4)
    for (ui64 e = start_index; e < end_index; e += 4) {}

    // Exit cleanly
    return 0;

}