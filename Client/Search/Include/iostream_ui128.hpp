#ifndef PARKER2_IOSTREAM_UI128_HPP
#define PARKER2_IOSTREAM_UI128_HPP

#include "types.hpp"
#include <iostream>

// Check if the ui128 type is available
#ifdef PARKER2_UI128_AVAILABLE

// ================================================================================================
// Overload the << operator to support printing of ui128 values
// ================================================================================================
std::ostream& operator<<(std::ostream& stream, ui128 value);

#endif

#endif