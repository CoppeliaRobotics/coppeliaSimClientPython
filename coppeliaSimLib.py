from ctypes import *
import builtins

coppeliaSimLib = cdll.LoadLibrary(builtins.coppeliaSim_library)
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

def simLoadBridge():
    stack = simCreateStack()
    simPushStringOntoStack(stack, c_char_p('python-client-bridge'.encode('ascii')), 0)
    r = simCallScriptFunctionEx(8, c_char_p('require'.encode('ascii')), stack)
    simReleaseStack(stack)

def simCallFunction(func, args):
    stack = simCreateStack()
    import cbor
    b = cbor.dumps({'func': func, 'args': args})
    simPushStringOntoStack(stack, c_char_p(b), len(b))
    r = simCallScriptFunctionEx(8, c_char_p('__call'.encode('ascii')), stack)
    sz = c_int()
    ptr = simGetStackStringValue(stack, byref(sz))
    o = cbor.loads(string_at(ptr, sz.value))
    simReleaseBuffer(ptr)
    simReleaseStack(stack)
    return o

__all__ = ['simLoadBridge', 'simCallFunction']

for name in dir(coppeliaSimLib):
    if name.startswith('sim'):
        f = getattr(coppeliaSimLib, name)
        if callable(f):
            globals()[name] = f
            __all__.append(name)