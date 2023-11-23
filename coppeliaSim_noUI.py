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

    import coppeliasim.cmdopt
    parser = argparse.ArgumentParser(description='CoppeliaSim client.')
    coppeliasim.cmdopt.add(parser, __file__, 'coppeliaSimHeadless')
    args = parser.parse_args()

    builtins.coppeliasim_library = args.coppeliasim_library
    from coppeliasim.lib import *

    appDir = os.path.dirname(args.coppeliasim_library)

    import coppeliasim.bridge
    
    simInitialize(c_char_p(appDir.encode('utf-8')), 0)

    coppeliasim.bridge.load()

    # fetch CoppeliaSim API sim-namespace functions:
    global sim
    sim = coppeliasim.bridge.require('sim')
    
    while not simGetExitRequest():
        simLoop(None, 0)
    simDeinitialize()

