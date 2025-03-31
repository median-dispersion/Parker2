# Compiler
CXX = g++

# Compiler flags
CXXFLAGS = -O3 -march=native -flto

# Libraries
LIBS = -lgmp -lgmpxx

# Source files
SRC = root.cpp

# Output executable
TARGET = root.out

# Default rule
all: $(TARGET)

# Linking and compilation
$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) $(SRC) $(LIBS) -o $(TARGET)

# Clean rule
clean:
	rm -f $(TARGET)