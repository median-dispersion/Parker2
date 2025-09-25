# Compiler
COMPILER = g++
COMPILER_FLAGS = -Wall -Wextra -Werror -O3 -march=native -flto -funroll-loops

# Libraries
LIBRARIES =

# Directories
SOURCE_DIRECTORY = ./Source
OBJECT_DIRECTORY = ./Build

# Files
SOURCES = $(wildcard $(SOURCE_DIRECTORY)/*.cpp)
OBJECTS = $(patsubst $(SOURCE_DIRECTORY)/%.cpp, $(OBJECT_DIRECTORY)/%.o, $(SOURCES))
TARGET  = ./search.out

# Default build rule
all: brahmaguptaFibonacciIdentity

# Direct (brute force) pair search method
directPairSearch: COMPILER_FLAGS += -DDIRECT_PAIR_SEARCH
directPairSearch: clean $(TARGET)

# Brahmagupta-Fibonacci identity method
brahmaguptaFibonacciIdentity: clean $(TARGET)

# Link object files to create executable
$(TARGET): $(OBJECTS)
	$(COMPILER) $(COMPILER_FLAGS) $^ $(LIBRARIES) -o $@

# Compile source files into object files
$(OBJECT_DIRECTORY)/%.o: $(SOURCE_DIRECTORY)/%.cpp | $(OBJECT_DIRECTORY)
	$(COMPILER) $(COMPILER_FLAGS) -c $< -o $@

# Create build directory if missing
$(OBJECT_DIRECTORY):
	mkdir -p $(OBJECT_DIRECTORY)

# Clean build artifacts
clean:
	rm -rf $(OBJECT_DIRECTORY) $(TARGET)