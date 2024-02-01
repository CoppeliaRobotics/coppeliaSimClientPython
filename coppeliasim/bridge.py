import ctypes
import functools


def importCalltipModule():
    # calltip module import magic:
    try:
        import calltip
        return calltip
    except ModuleNotFoundError:
        from pathlib import Path

        moduleDir = Path(__file__).parent  # 'coppeliasim' python module
        p = []

        # when used from the coppeliaSimClientPython dir inside programming/:
        programmingDir = moduleDir.parent.parent
        p.append(programmingDir / 'include' / 'python')

        # when used from the installed <coppeliaSim>/python/ dir:
        resourcesDir = moduleDir.parent.parent
        p.append(resourcesDir / 'programming' / 'include' / 'python')

        # if COPPELIASIM_ROOT_DIR is defined:
        import os
        if rootDir := os.environ.get('COPPELIASIM_ROOT_DIR'):
            p.append(Path(rootDir) / 'programming' / 'include' / 'python')

        import sys
        for path in p:
            if (path / 'calltip.py').is_file():
                sys.path.append(str(path))
                break

        import calltip
        return calltip


def load():
    call('require', ('scriptClientBridge',))


@functools.cache
def getTypeHints(func):
    calltip = importCalltipModule()
    c = call('sim.getApiInfo', [-1, func], (('int', 'string'), ('string')))
    if not c:
        return (None, None)
    c = c.split('\n')[0]
    fd = calltip.FuncDef.from_calltip(c)
    return (
        tuple(item.type for item in fd.in_args),
        tuple(item.type for item in fd.out_args),
    )


def call(func, args, typeHints=None):
    if typeHints is None:
        typeHints = getTypeHints(func)
    from coppeliasim.lib import (
        simCreateStack,
        simCallScriptFunctionEx,
        simReleaseStack,
        sim_scripttype_sandboxscript,
    )
    import coppeliasim.stack as stack
    stackHandle = simCreateStack()
    stack.write(stackHandle, args, typeHints[0])
    s = sim_scripttype_sandboxscript
    f = ctypes.c_char_p(f'{func}@lua'.encode('ascii'))
    r = simCallScriptFunctionEx(s, f, stackHandle)
    if r == -1:
        if False:
            what = f'simCallScriptFunctionEx({s}, {func!r}, {args!r})'
        else:
            what = 'simCallScriptFunctionEx'
        raise Exception(f'{what} returned -1')
    ret = stack.read(stackHandle, typeHints[1])
    simReleaseStack(stackHandle)
    if len(ret) == 1:
        return ret[0]
    elif len(ret) > 1:
        return ret


def getObject(name, _info=None):
    ret = type(name, (), {})
    if not _info:
        _info = call('scriptClientBridge.info', [name])
    for k, v in _info.items():
        if not isinstance(v, dict):
            raise ValueError('found nondict')
        if len(v) == 1 and 'func' in v:
            if f'{name}.{k}' == 'sim.getScriptFunctions':
                setattr(ret, k, lambda scriptHandle:
                        type('', (object,), {
                            '__getattr__':
                                lambda _, func:
                                    lambda *args:
                                        call('sim.callScriptFunction', (func, scriptHandle) + args)
                        })())
                continue
            setattr(ret, k, lambda *a, func=f'{name}.{k}': call(func, a))
        elif len(v) == 1 and 'const' in v:
            setattr(ret, k, v['const'])
        else:
            setattr(ret, k, getObject(f'{name}.{k}', _info=v))
    return ret


def require(obj):
    call('scriptClientBridge.require', [obj])
    o = getObject(obj)
    return o
