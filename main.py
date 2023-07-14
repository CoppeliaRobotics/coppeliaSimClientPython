# need to set DYLD_LIBRARY_PATH=$PWD/../Frameworks
# to avoid libraries load errors

from ctypes import *
import argparse
import threading
import os
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CoppeliaSim client.')
    parser.add_argument('coppeliaSim_library', type=str, help='Path to the coppeliaSim shared library')
    args = parser.parse_args()

    builtins.coppeliaSim_library = args.coppeliaSim_library
    from coppeliaSimLib import *

    appDir = os.path.dirname(args.coppeliaSim_library)

    simInitialize(c_char_p(appDir.encode('utf-8')), 0)
    while not simGetExitRequest():
        simLoop(None, 0)
    simDeinitialize()
