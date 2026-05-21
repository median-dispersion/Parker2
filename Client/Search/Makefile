# Directories
INCLUDE_DIRECTORY = ./Include
SOURCE_DIRECTORY = ./Source
LIBRARIES_DIRECTORY = ./Libraries
BUILD_DIRECTORY = ./Build

# Compiler
COMPILER = g++
COMPILER_FLAGS = -std=c++23 -Wall -Wextra -Werror -O3 -march=native -flto

# Files and paths
INCLUDES = -I$(INCLUDE_DIRECTORY) $(addprefix -I, $(wildcard $(LIBRARIES_DIRECTORY)/*/Include))
SOURCES = $(shell find $(SOURCE_DIRECTORY) -type f -name '*.cpp') $(shell find $(LIBRARIES_DIRECTORY) -type f -name '*.cpp')
OBJECTS = $(patsubst %.cpp, $(BUILD_DIRECTORY)/%.o, $(SOURCES))
TARGET = main

# Default build rule
all: clean $(TARGET)

# Link object files to create executable
$(TARGET): $(OBJECTS)
	$(COMPILER) $(COMPILER_FLAGS) $^ -o $@

# Compile source files into object files
$(BUILD_DIRECTORY)/%.o: %.cpp
	mkdir -p $(dir $@)
	$(COMPILER) $(COMPILER_FLAGS) $(INCLUDES) -c $< -o $@

# Clean build artifacts
clean:
	rm -rf $(BUILD_DIRECTORY) $(TARGET)