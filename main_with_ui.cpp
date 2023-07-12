#include <string>
#include <filesystem>
#include <thread>
#include <simLib/simLib.h>

void simThreadFunc()
{
    std::string appDir = std::filesystem::current_path().string();
    simInitialize(appDir.c_str(), 0);
    while(!simGetExitRequest())
        simLoop(nullptr, 0);
    simDeinitialize();
}

int main(int argc,char* argv[])
{
    LIBRARY simLib=loadSimLibrary("libcoppeliaSim.dylib");
    getSimProcAddresses(simLib);

    std::thread t(simThreadFunc);
    int options=sim_gui_all;
    simRunGui(options);
    t.join();

    unloadSimLibrary(simLib);
    return 0;
}
