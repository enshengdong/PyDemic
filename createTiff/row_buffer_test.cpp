#include "row_buffer.h"
#include <iostream>

int main() {
    row_buffer<int> arr(3, 3);
    int y = 0;
    for (auto i : arr) {
        int x = 0;
        for (auto& j : i) {
            j = (x++) + y;
        }
        y += 10;
    }
    for (auto&i : arr.all()) {
        std::cout << ++i << std::endl;
    }
    return 0;
}

