// This is a temporary dummy search!

#include <iostream>
#include <thread>
#include <chrono>

int main() {

    for (int i = 0; i < 300; i++) {

        std::cout << "{\"current_index\":" << i << "}" << std::endl;

        std::this_thread::sleep_for(std::chrono::seconds(1));

    }

    std::cout << "{\"result\":{\"a\":1,\"b\":2,\"c\":3,\"d\":4,\"e\":5,\"f\":6,\"g\":7,\"h\":8,\"i\":9}}" << std::endl;

    return 0;

}