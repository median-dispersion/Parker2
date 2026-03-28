// This is a temporary dummy search!

#include <iostream>
#include <thread>
#include <chrono>

int main() {

    for (int i = 0; i < 300; i++) {

        std::cout << "{\"current_index\":" << i << "}" << std::endl;

        std::this_thread::sleep_for(std::chrono::seconds(1));

    }

    return 0;

}