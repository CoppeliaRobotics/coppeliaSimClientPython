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
        simRegCallback,
    )
    import coppeliasim.stack
    import coppeliasim.bridge

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

    @coppeliasim.stack.callback
    def myCallback(state, data):
        print('myCallback called with args:', state, data)
        return True  # i.e. valid config

    simInitialize(appDir().encode('utf-8'), 0)

    try:
        coppeliasim.bridge.load()

        # fetch CoppeliaSim API sim-namespace functions:
        global sim
        sim = coppeliasim.bridge.require('sim')
        simIK = coppeliasim.bridge.require('simIK')

        v = sim.getInt32Param(sim.intparam_program_full_version)
        version = '.'.join(str(v // 100**(3-i) % 100) for i in range(4))
        print('CoppeliaSim version is:', version)

        testScene = str(Path(__file__).parent / 'various.ttt')
        sim.loadScene(testScene)

        from ctypes import CFUNCTYPE, c_int
        myCallback_c = CFUNCTYPE(c_int, c_int)(myCallback)
        simRegCallback(0, myCallback_c)

        simJointHandles = []
        robot = sim.getObject('/LBR4p')
        for i in range(7):
            simJointHandles.append(sim.getObject('./j', {'index': i, 'proxy': robot}))
        simTip = sim.getObject('./tip', {'proxy': robot})
        simBase = robot
        simTarget = sim.getObject('./target', {'proxy': robot})
        target = sim.getObject('./testTarget5', {'proxy': robot})

        sensor1 = sim.getObject('/sensor1')
        sensor2 = sim.getObject('/sensor2')
        cameraJointScript = sim.getObject('/cameraJoint/script')
        funcs = sim.getScriptFunctions(cameraJointScript)
        mesh = sim.getObject('/mesh')

        ikEnv = simIK.createEnvironment()

        ikGroup = simIK.createGroup(ikEnv)
        ikElement, simToIkObjectMapping, ikToSimObjectMapping = simIK.addElementFromScene(ikEnv, ikGroup, simBase, simTip, simTarget, simIK.constraint_pose)
        simIK.setElementPrecision(ikEnv, ikGroup, ikElement, [0.00005, 0.0017])
        ikJointHandles = []
        for i in range(7):
            ikJointHandles.append(simToIkObjectMapping[simJointHandles[i]])
        ikTarget = simToIkObjectMapping[simTarget]
        ikBase = simToIkObjectMapping[simBase]

        simStart()  # start simulation
        for c in range(200):
            simIK.setObjectMatrix(ikEnv, ikTarget, sim.getObjectMatrix(target, simBase), ikBase)

            state = simIK.findConfig(ikEnv, ikGroup, ikJointHandles, 0.25, 0.1, [1, 1, 1, 0.1], 'ccallback0', simJointHandles)
            if state:
                for i in range(7):
                    sim.setJointPosition(simJointHandles[i], state[i])

            img, res = sim.getVisionSensorImg(sensor1)
            sim.setVisionSensorImg(sensor2, img)

            if c == 150:
                funcs.stopJointMotion()

            simStep()
        simStop()  # stop simulation and wait until really stopped

        info = sim.getShapeViz(mesh, 0)
        #print(info)

    except Exception:
        import traceback
        print(traceback.format_exc())

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
