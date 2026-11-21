#ifndef PARKER2_HELPER_FUNCTIONS_HPP
#define PARKER2_HELPER_FUNCTIONS_HPP

#include <iostream>
#include "types.hpp"

// ================================================================================================
// Overload the << operator to support printing of unsigned 128-bit integers
// ================================================================================================
std::ostream& operator<<(std::ostream& stream, ui128 value);

#endif