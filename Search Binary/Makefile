# Compiler
COMPILER = g++
COMPILER_FLAGS = -Wall -Wextra -Werror -O3 -march=native -flto -funroll-loops

# Files
SOURCE = ./main.cpp
TARGET = ./search.out

# Build target
all:
	$(COMPILER) $(COMPILER_FLAGS) $(SOURCE) -o $(TARGET)

# Clean build target
clean:
	rm -rf $(TARGET)