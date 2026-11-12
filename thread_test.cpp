#include <iostream>
#include <thread>

void sayHello() {
    std::cout << "Hello from a thread\n";
}

int main() {
    std::thread t(sayHello);
    t.join();
    std::cout << "Thread finished\n";
    return 0;
}