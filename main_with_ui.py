# need to set DYLD_LIBRARY_PATH=$PWD/../Frameworks
# to avoid libraries load errors

import argparse
import builtins
import os
import sys
import threading

from ctypes import *


def simStart():
    if sim.getSimulationState() == sim.simulation_stopped:
        sim.startSimulation()

def simStep():
    if sim.getSimulationState() != sim.simulation_stopped:
        t = sim.getSimulationTime()
        while t == sim.getSimulationTime():
            simLoop(None, 0)

def simStop():
    while sim.getSimulationState() != sim.simulation_stopped:
        sim.stopSimulation()
        simLoop(None, 0)

def simThreadFunc(appDir):
    import coppeliaSim.bridge

    simInitialize(c_char_p(appDir.encode('utf-8')), 0)

    coppeliaSim.bridge.load()

    # fetch CoppeliaSim API sim-namespace functions:
    global sim
    sim = coppeliaSim.bridge.require('sim')

    v = sim.getInt32Param(sim.intparam_program_full_version)
    version = '.'.join(str(v // 100**(3-i) % 100) for i in range(4))
    print('CoppeliaSim version is:', version)

    # example: load a scene, run the simulation for 1000 steps, then quit:
    '''
    sim.loadScene('path/to/scene.ttt')
    simStart()
    for i in range(1000):
        t = sim.getSimulationTime()
        print(f'Simulation time: {t:.2f} [s] (simulation running synchronously to client, i.e. stepped)')
        simStep()
    simStop()
    simDeinitialize()
    '''

    # example: simply run CoppeliaSim:
    while not simGetExitRequest():
        simLoop(None, 0)
    simDeinitialize()

if __name__ == '__main__':
    import coppeliaSim.commandLineOptions
    parser = argparse.ArgumentParser(description='CoppeliaSim client.')
    coppeliaSim.commandLineOptions.add(parser)
    args = parser.parse_args()

    builtins.coppeliaSim_library = args.coppeliasim_library
    from coppeliaSim.lib import *

    options = coppeliaSim.commandLineOptions.parse(args)

    appDir = os.path.dirname(args.coppeliasim_library)

    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = appDir

    t = threading.Thread(target=simThreadFunc, args=(appDir,))
    t.start()
    simRunGui(options)
    t.join()
