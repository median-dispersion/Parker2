#include "iostream_ui128.hpp"
#include "types.hpp"
#include <iostream>
#include <string>
#include <algorithm>

// Check if the ui128 type is available
#ifdef PARKER2_UI128_AVAILABLE

// ================================================================================================
// Overload the << operator to support printing of ui128 values
// ================================================================================================
std::ostream& operator<<(std::ostream& stream, ui128 value) {

    // If the value is zero print "0"
    if (value == 0) { return stream << "0"; }

    // Initialize the output string
    std::string string;

    // Loop as long as there are digits remaining in the value
    while (value) {

        // Add the last digit of the value to the string
        string.push_back('0' + (value % 10));

        // Remove the last digit from the value by dividing it by 10
        value /= 10;

    }

    // Reverse the string to get correct order of digits
    std::reverse(string.begin(), string.end());

    // Print the string
    return stream << string;

}

#endif