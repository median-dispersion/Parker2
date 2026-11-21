#include "helper_functions.hpp"
#include <iostream>
#include "types.hpp"
#include <string>
#include <algorithm>

// ================================================================================================
// Overload the << operator to support printing of unsigned 128-bit integers
// ================================================================================================
std::ostream& operator<<(std::ostream& stream, ui128 value) {

    // If the value is zero print "0"
    if (value == 0) { return stream << "0"; }

    // Initialize the output string
    std::string string;

    // Loop as long as there are digits remaining in the value
    while (value) {

        // Add the last digit of the value to the string
        // Offset the value by 48 to get the correct decimal representation of the ASCII character
        string.push_back(48 + (value % 10));

        // Remove the last digit from the value by dividing it by 10
        value /= 10;

    }

    // Reverse the string to get correct order of digits
    std::reverse(string.begin(), string.end());

    // Print the string
    return stream << string;

}