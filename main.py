# need to set DYLD_LIBRARY_PATH=$PWD/../Frameworks
# to avoid libraries load errors

import argparse
import builtins
import os
import sys
import threading

from ctypes import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CoppeliaSim client.')
    parser.add_argument('coppeliaSim_library', type=str, help='Path to the coppeliaSim shared library')
    args = parser.parse_args()

    builtins.coppeliaSim_library = args.coppeliaSim_library
    from coppeliaSimLib import *

    appDir = os.path.dirname(args.coppeliaSim_library)

    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = appDir

    simInitialize(c_char_p(appDir.encode('utf-8')), 0)
    while not simGetExitRequest():
        simLoop(None, 0)
    simDeinitialize()
