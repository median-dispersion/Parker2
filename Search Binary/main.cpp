#include <cstdint>
#include <string>
#include <cmath>
#include <iostream>

using namespace std;

bool isPerfectSquare(int64_t number) {

    if (number < 0) return false;

    int64_t root = sqrt(number);

    return root * root == number;

}

int main(int, char* argv[]) {

    int64_t start = stoll(argv[1]);
    int64_t end   = stoll(argv[2]);

    for (int64_t e = start; e < end; e++) {

        int64_t squareLimit = ceil(sqrt(2) * e);
        int64_t eSquared    = e * e;

        for (int64_t a = e + 1; a < squareLimit; a++) {

            int64_t aSquared = a * a;
            int64_t x        = aSquared - eSquared;
            int64_t iSquared = eSquared - x;

            if (isPerfectSquare(iSquared)) {

                for (int64_t c = a; c < squareLimit; c++) {

                    int64_t cSquared = c * c;
                    int64_t y        = cSquared - eSquared;
                    int64_t gSquared = eSquared - y;

                    if (isPerfectSquare(gSquared)) {

                        int64_t bSquared = eSquared - x - y;

                        if (isPerfectSquare(bSquared)) {

                            int64_t dSquared = eSquared - x + y;

                            if (isPerfectSquare(dSquared)) {

                                int64_t fSquared = eSquared + x - y;

                                if (isPerfectSquare(fSquared)) {

                                    int64_t hSquared = eSquared + x + y;

                                    if (isPerfectSquare(hSquared)) {

                                        cout << "{\"result\": 0, \"e\": " << e << ", \"x\": " << x << ", \"y\": " << y << "}" << endl;

                                    }

                                }

                            }

                        }

                    }

                }

            }

        }

    }

    return 0;

}