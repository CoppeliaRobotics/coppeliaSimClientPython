# need to set DYLD_LIBRARY_PATH=$PWD/../Frameworks
# to avoid libraries load errors

import argparse
import threading

from pathlib import Path


# refer to the manual (en/coppeliaSimLibrary.htm) for customization examples


def simThreadFunc():
    from coppeliasim.lib import (
        appDir,
        simInitialize,
        simLoop,
        simDeinitialize,
        simGetExitRequest,
    )

    simInitialize(appDir().encode('utf-8'), 0)

    while not simGetExitRequest():
        simLoop(None, 0)

    simDeinitialize()


if __name__ == '__main__':
    import coppeliasim.cmdopt
    parser = argparse.ArgumentParser(description='CoppeliaSim client.', add_help=False)
    coppeliasim.cmdopt.add(parser)
    args = parser.parse_args()
    options = coppeliasim.cmdopt.read_args(args)

    if args.true_headless:
        simThreadFunc()
    else:
        from coppeliasim.lib import simRunGui
        t = threading.Thread(target=simThreadFunc)
        t.start()
        simRunGui(options)
        t.join()
