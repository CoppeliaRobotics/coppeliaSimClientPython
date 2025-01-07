# macOS: need to set DYLD_LIBRARY_PATH=$PWD/../Frameworks
#        to avoid libraries load errors

import argparse
import sys

from pathlib import Path


def simThreadFunc():
    from coppeliasim.lib import (
        appDir,
        simInitialize,
        simLoop,
        simDeinitialize,
        simGetExitRequest,
    )

    simInitialize(appDir().encode('utf-8'), 0)

    import coppeliasim.bridge
    coppeliasim.bridge.load()
    global sim, simOMPL
    sim = coppeliasim.bridge.require('sim')
    simOMPL = coppeliasim.bridge.require('simOMPL')

    global omplTask, collisionPairs
    omplTask = None
    collisionPairs = None

    import coppeliasim.stack
    @coppeliasim.stack.callback
    def stateValidation(state):
        global omplTask, collisionPairs
        if omplTask is None:
            omplTask = sim.getStringProperty(sim.handle_scene, 'signal.omplTask')
        if collisionPairs is None:
            collisionPairs = [
                sim.getIntProperty(sim.handle_scene, 'signal.omplColl1'),
                sim.getIntProperty(sim.handle_scene, 'signal.omplColl2'),
            ]

        maxDistance = 0.05
        minDistance = 0.01

        print(f'called stateValidation({state})')
        savedState = simOMPL.readState(omplTask)
        simOMPL.writeState(omplTask, state)

        res, d, objs = sim.checkDistance(collisionPairs[0], collisionPairs[1], maxDistance)
        p = res == 1 and d[6] > minDistance

        simOMPL.writeState(omplTask, savedState)

        return p

    from coppeliasim.lib import simRegCallback
    from ctypes import CFUNCTYPE, c_int
    cb = CFUNCTYPE(c_int, c_int)(stateValidation)
    simRegCallback(0, cb)

    sceneFile = str(Path(__file__).parent / 'ompl-callback.ttt')
    sim.loadScene(sceneFile)
    sim.startSimulation()

    while not simGetExitRequest():
        simLoop(None, 0)

    simDeinitialize()


if __name__ == '__main__':
    # allow running from repo directly:
    if (d := Path(__file__).absolute().parent).name == 'tests':
        sys.path.append(str(d.parent))

    import coppeliasim.cmdopt
    parser = argparse.ArgumentParser(description='CoppeliaSim client.', add_help=False)
    coppeliasim.cmdopt.add(parser)
    args = parser.parse_args()

    # set builtins.coppeliasim_library according to command line options:
    options = coppeliasim.cmdopt.read_args(args)

    if args.true_headless:
        simThreadFunc()
    else:
        import threading
        from coppeliasim.lib import simRunGui
        t = threading.Thread(target=simThreadFunc)
        t.start()
        simRunGui(options)
        t.join()
