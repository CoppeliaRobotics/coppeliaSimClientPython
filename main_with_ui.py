# need to set DYLD_LIBRARY_PATH=$PWD/../Frameworks
# to avoid libraries load errors

from ctypes import *
import argparse
import builtins
import threading
import os
import sys

def simThreadFunc(appDir):
    simInitialize(c_char_p(appDir.encode('utf-8')), 0)

    bridge.load()

    # example: call an API function:
    print(bridge.call('sim.getStringParam', [141]))

    while not simGetExitRequest():
        simLoop(None, 0)
    simDeinitialize()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CoppeliaSim client.')
    parser.add_argument('coppeliaSim_library', type=str, help='Path to the coppeliaSim shared library')
    parser.add_argument('-H', '--headless', action='store_true')
    args = parser.parse_args()

    builtins.coppeliaSim_library = args.coppeliaSim_library
    from coppeliaSimLib import *
    import coppeliaSimLib_bridge as bridge

    appDir = os.path.dirname(args.coppeliaSim_library)

    import os
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = appDir

    t = threading.Thread(target=simThreadFunc, args=(appDir,))
    t.start()
    sim_gui_all = 0x0ffff
    sim_gui_headless = 0x10000
    options = sim_gui_headless if args.headless else sim_gui_all
    simRunGui(options)
    t.join()
