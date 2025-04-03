CXX = g++

CXXFLAGS = -O3 -march=native -flto

all: limited #unlimited

limited:
	$(CXX) $(CXXFLAGS) limited.cpp -o limited.out

#unlimited:
#	$(CXX) $(CXXFLAGS) unlimited.cpp -lgmp -lgmpxx -o unlimited.out

clean:
	rm -f *.out

rebuild: clean all