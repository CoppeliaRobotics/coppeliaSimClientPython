# need to set DYLD_LIBRARY_PATH=$PWD/../Frameworks
# to avoid libraries load errors

import argparse
import builtins
import ctypes
import os
import sys
import threading

from pathlib import Path


# refer to the manual (en/coppeliaSimLibrary.htm) for customization examples


def simThreadFunc(appDir):
    from coppeliasim.lib import (
        simInitialize,
        simLoop,
        simDeinitialize,
        simGetExitRequest,
        simGetStringParam,
        simReleaseBuffer,
        sim_stringparam_pythondir,
    )

    simInitialize(ctypes.c_char_p(appDir.encode('utf-8')), 0)

    while not simGetExitRequest():
        simLoop(None, 0)

    simDeinitialize()


if __name__ == '__main__':
    import coppeliasim.cmdopt
    parser = argparse.ArgumentParser(description='CoppeliaSim client.', add_help=False)
    coppeliasim.cmdopt.add(parser)
    args = parser.parse_args()
    if args.coppeliasim_library == 'default':
        defaultLibNameBase = 'coppeliaSim'
        if args.true_headless:
            defaultLibNameBase = 'coppeliaSimHeadless'
        from pathlib import Path
        libPath = Path(__file__).absolute().parent
        import platform
        plat = platform.system()
        if plat == 'Windows':
            libPath /= f'{defaultLibNameBase}.dll'
        elif plat == 'Linux':
            libPath /= f'lib{defaultLibNameBase}.so'
        elif plat == 'Darwin':
            libPath /= f'../MacOS/lib{defaultLibNameBase}.dylib'
        args.coppeliasim_library = str(libPath)

    builtins.coppeliasim_library = args.coppeliasim_library

    options = coppeliasim.cmdopt.parse(args)

    appDir = os.path.dirname(args.coppeliasim_library)

    if args.true_headless:
        simThreadFunc(appDir)
    else:
        from coppeliasim.lib import simRunGui
        t = threading.Thread(target=simThreadFunc, args=(appDir,))
        t.start()
        simRunGui(options)
        t.join()
