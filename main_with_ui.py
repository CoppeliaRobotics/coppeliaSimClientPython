# need to set DYLD_LIBRARY_PATH=$PWD/../Frameworks
# to avoid libraries load errors

from ctypes import *
import argparse
import threading
import os
import sys

def simThreadFunc(appDir):
    coppeliaSimLib.simInitialize(c_char_p(appDir.encode('utf-8')), 0)

    #stack = coppeliaSimLib.simCreateStack()
    #r = coppeliaSimLib.simCallScriptFunctionEx(8, c_char_p('foo'.encode('ascii')), stack)
    #coppeliaSimLib.simReleaseStack(stack)

    while not coppeliaSimLib.simGetExitRequest():
        coppeliaSimLib.simLoop(None, 0)
    coppeliaSimLib.simDeinitialize()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CoppeliaSim client.')
    parser.add_argument('coppeliaSim_library', type=str, help='Path to the coppeliaSim shared library')
    parser.add_argument('-H', '--headless', action='store_true')
    args = parser.parse_args()

    coppeliaSimLib = cdll.LoadLibrary(args.coppeliaSim_library)
    appDir = os.path.dirname(args.coppeliaSim_library)

    t = threading.Thread(target=simThreadFunc, args=(appDir,))
    t.start()
    sim_gui_all = 0x0ffff
    sim_gui_headless = 0x10000
    options = sim_gui_headless if args.headless else sim_gui_all
    coppeliaSimLib.simRunGui(options)
    t.join()
