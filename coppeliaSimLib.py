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

class simBridge:
    @staticmethod
    def load():
        stack = simCreateStack()
        simPushStringOntoStack(stack, c_char_p('scriptClientBridge'.encode('ascii')), 0)
        r = simCallScriptFunctionEx(8, c_char_p('require'.encode('ascii')), stack)
        simReleaseStack(stack)

    @staticmethod
    def call(func, args):
        stack = simCreateStack()
        import cbor
        b = cbor.dumps({'func': func, 'args': args})
        simPushStringOntoStack(stack, c_char_p(b), len(b))
        r = simCallScriptFunctionEx(8, c_char_p('scriptClientBridge.call'.encode('ascii')), stack)
        sz = c_int()
        ptr = simGetStackStringValue(stack, byref(sz))
        o = cbor.loads(string_at(ptr, sz.value))
        simReleaseBuffer(ptr)
        simReleaseStack(stack)
        if o['success']:
            ret = o['result']
            if len(ret) == 1:
                return ret[0]
            if len(ret) > 1:
                return tuple(ret)
        else:
            raise Exception(o['error'])

    @staticmethod
    def getObject(name, _info=None):
        ret = type(name, (), {})
        if not _info:
            _info = simBridge.call('scriptClientBridge.info', [name])
        for k, v in _info.items():
            if not isinstance(v, dict):
                raise ValueError('found nondict')
            if len(v) == 1 and 'func' in v:
                setattr(ret, k, lambda *a, func=f'{name}.{k}': simBridge.call(func, a))
            elif len(v) == 1 and 'const' in v:
                setattr(ret, k, v['const'])
            else:
                setattr(ret, k, simBridge.getObject(f'{name}.{k}', _info=v))
        return ret

    @staticmethod
    def require(obj):
        o = simBridge.getObject(obj)
        return o

__all__ = ['simBridge']

for name in dir(coppeliaSimLib):
    if name.startswith('sim') and name != 'simBridge':
        f = getattr(coppeliaSimLib, name)
        if callable(f):
            globals()[name] = f
            __all__.append(name)
