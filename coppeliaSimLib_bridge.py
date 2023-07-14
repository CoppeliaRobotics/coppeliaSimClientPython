from ctypes import *
from coppeliaSimLib import *

def load():
    stack = simCreateStack()
    simPushStringOntoStack(stack, c_char_p('python-client-bridge'.encode('ascii')), 0)
    r = simCallScriptFunctionEx(8, c_char_p('require'.encode('ascii')), stack)
    simReleaseStack(stack)

def call(func, args):
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
