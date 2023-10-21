import builtins
import os
import sys

from ctypes import *


if not os.path.isfile(builtins.coppeliasim_library):
    print(f'{os.path.basename(sys.argv[0])}: error: the specified coppeliaSim library does not exist: {builtins.coppeliasim_library}')
    sys.exit(1)

appDir = os.path.dirname(builtins.coppeliasim_library)
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = appDir

import platform
plat = platform.system()
if plat == 'Darwin':
    fd = os.path.normpath(appDir + '/../Frameworks')
    os.environ['DYLD_LIBRARY_PATH'] = fd + ':' + os.environ.get('DYLD_LIBRARY_PATH', '')
    print(f'If next step fails, do: export DYLD_LIBRARY_PATH={fd}:$DYLD_LIBRARY_PATH and relaunch.')

coppeliaSimLib = cdll.LoadLibrary(builtins.coppeliasim_library)
coppeliaSimLib.simRunGui.argtypes = [c_int]
coppeliaSimLib.simRunGui.restype = None
coppeliaSimLib.simCreateStack.argtypes = []
coppeliaSimLib.simCreateStack.restype = c_int
coppeliaSimLib.simReleaseStack.argtypes = [c_int]
coppeliaSimLib.simReleaseStack.restype = c_int
coppeliaSimLib.simReleaseBuffer.argtypes = [c_void_p]
coppeliaSimLib.simReleaseBuffer.restype = c_int
coppeliaSimLib.simPushStringOntoStack.argtypes = [c_int, c_char_p, c_int]
coppeliaSimLib.simPushStringOntoStack.restype = c_int
coppeliaSimLib.simCallScriptFunctionEx.argtypes = [c_int, c_char_p, c_int]
coppeliaSimLib.simCallScriptFunctionEx.restype = c_int
coppeliaSimLib.simGetStackStringValue.argtypes = [c_int, POINTER(c_int)]
coppeliaSimLib.simGetStackStringValue.restype = c_void_p
coppeliaSimLib.simInitialize.argtypes = [c_char_p, c_int]
coppeliaSimLib.simInitialize.restype = c_int
coppeliaSimLib.simGetExitRequest.argtypes = []
coppeliaSimLib.simGetExitRequest.restype = c_int
coppeliaSimLib.simLoop.argtypes = [c_void_p, c_int]
coppeliaSimLib.simLoop.restype = c_int
coppeliaSimLib.simDeinitialize.argtypes = []
coppeliaSimLib.simDeinitialize.restype = c_int
coppeliaSimLib.simSetStringParam.argtypes = [c_int, c_char_p]
coppeliaSimLib.simSetStringParam.restype = c_int
coppeliaSimLib.simSetNamedStringParam.argtypes = [c_char_p, c_char_p, c_int]
coppeliaSimLib.simSetNamedStringParam.restype = c_int

__all__ = []

for name in dir(coppeliaSimLib):
    if name.startswith('sim'):
        f = getattr(coppeliaSimLib, name)
        if callable(f):
            globals()[name] = f
            __all__.append(name)
