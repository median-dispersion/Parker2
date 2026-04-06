# Directories
INCLUDE_DIRECTORY = ./Include
SOURCE_DIRECTORY = ./Source
OBJECT_DIRECTORY = ./Build

# Compiler
COMPILER = g++
COMPILER_FLAGS = -std=c++20 -Wall -Wextra -Werror -O3 -march=native -flto -funroll-loops -I$(INCLUDE_DIRECTORY)

# Libraries
LIBRARIES = -lgmp -lgmpxx

# Files
SOURCES = $(wildcard $(SOURCE_DIRECTORY)/*.cpp)
OBJECTS = $(patsubst $(SOURCE_DIRECTORY)/%.cpp, $(OBJECT_DIRECTORY)/%.o, $(SOURCES))
TARGET = ./main

# Default build rule
all: clean $(TARGET)

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