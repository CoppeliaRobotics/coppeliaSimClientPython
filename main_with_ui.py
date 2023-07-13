# need to set DYLD_LIBRARY_PATH=$PWD/../Frameworks
# to avoid libraries load errors

from ctypes import *
import argparse
import threading
import os
import sys

def simThreadFunc(appDir):
    coppeliaSimLib.simInitialize(c_char_p(appDir.encode('utf-8')), 0)
    while not coppeliaSimLib.simGetExitRequest():
        coppeliaSimLib.simLoop(None, 0)
    coppeliaSimLib.simDeinitialize()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CoppeliaSim client.')
    parser.add_argument('coppeliaSim_library', type=str, help='Path to the coppeliaSim shared library')
    args = parser.parse_args()

    coppeliaSimLib = cdll.LoadLibrary(args.coppeliaSim_library)
    appDir = os.path.dirname(args.coppeliaSim_library)

    t = threading.Thread(target=simThreadFunc, args=(appDir,))
    t.start()
    options = 0x0ffff # sim_gui_all
    coppeliaSimLib.simRunGui(options)
    t.join()
