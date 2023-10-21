# need to set DYLD_LIBRARY_PATH=$PWD/../Frameworks
# to avoid libraries load errors

import argparse
import builtins
import os
import sys
import threading

from pathlib import Path
from ctypes import *


if __name__ == '__main__':
    sys.path.append(str(Path(__file__).absolute().parent / 'python'))

    parser = argparse.ArgumentParser(description='CoppeliaSim client.')
    coppeliasim.cmdopt.add(parser, __file__)
    args = parser.parse_args()

    builtins.coppeliasim_library = args.coppeliasim_library
    from coppeliasim.lib import *

    appDir = os.path.dirname(args.coppeliasim_library)

    simInitialize(c_char_p(appDir.encode('utf-8')), 0)
    while not simGetExitRequest():
        simLoop(None, 0)
    simDeinitialize()
