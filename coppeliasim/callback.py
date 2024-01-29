import ctypes


def read_null_from_stack(stack):
    from coppeliasim.lib import (
        simGetStackItemType,
        simPopStackItem,
        sim_stackitem_null,
    )
    if simGetStackItemType(stack, -1) == sim_stackitem_null:
        simPopStackItem(stack, 1)
        return None
    else:
        raise RuntimeError('expected nil')

def read_bool_from_stack(stack):
    from coppeliasim.lib import (
        simGetStackBoolValue,
        simPopStackItem,
    )
    value = ctypes.c_bool()
    if simGetStackBoolValue(stack, ctypes.byref(value)) == 1:
        simPopStackItem(stack, 1)
        return value.value
    else:
        raise RuntimeError('expected bool')

def read_int_from_stack(stack):
    from coppeliasim.lib import (
        simGetStackInt32Value,
        simPopStackItem,
    )
    value = ctypes.c_int()
    if simGetStackInt32Value(stack, ctypes.byref(value)) == 1:
        simPopStackItem(stack, 1)
        return value.value
    else:
        raise RuntimeError('expected int')

def read_long_from_stack(stack):
    from coppeliasim.lib import (
        simGetStackInt64Value,
        simPopStackItem,
    )
    value = ctypes.c_longlong()
    if simGetStackInt64Value(stack, ctypes.byref(value)) == 1:
        simPopStackItem(stack, 1)
        return value.value
    else:
        raise RuntimeError('expected int64')

def read_double_from_stack(stack):
    from coppeliasim.lib import (
        simGetStackDoubleValue,
        simPopStackItem,
    )
    value = ctypes.c_double()
    if simGetStackDoubleValue(stack, ctypes.byref(value)) == 1:
        simPopStackItem(stack, 1)
        return value.value
    else:
        raise RuntimeError('expected double')

def read_string_from_stack(stack):
    from coppeliasim.lib import (
        simGetStackStringValue,
        simReleaseBuffer,
        simPopStackItem,
    )
    string_size = ctypes.c_int()
    string_ptr = simGetStackStringValue(stack, ctypes.byref(string_size))
    string_value = ctypes.string_at(string_ptr, string_size.value)
    simPopStackItem(stack, 1)
    value = string_value.decode('utf-8')
    simReleaseBuffer(string_ptr)
    return value

def read_dict_from_stack(stack):
    from coppeliasim.lib import (
        simGetStackTableInfo,
        simGetStackSize,
        simUnfoldStackTable,
        simMoveStackItemToTop,
        sim_stack_table_map,
        sim_stack_table_empty,
    )
    d = dict()
    info = simGetStackTableInfo(stack, 0)
    if info != sim_stack_table_map and info != sim_stack_table_empty:
        raise RuntimeError('expected a map')
    oldsz = simGetStackSize(stack)
    simUnfoldStackTable(stack)
    n = (simGetStackSize(stack) - oldsz + 1) // 2
    for i in range(n):
        simMoveStackItemToTop(stack, oldsz - 1)
        k = read_value_from_stack(stack)
        simMoveStackItemToTop(stack, oldsz - 1)
        d[k] = read_value_from_stack(stack)
    return d

def read_list_from_stack(stack):
    from coppeliasim.lib import (
        simGetStackSize,
        simUnfoldStackTable,
        simMoveStackItemToTop,
    )
    l = list()
    oldsz = simGetStackSize(stack)
    simUnfoldStackTable(stack)
    n = (simGetStackSize(stack) - oldsz + 1) // 2
    for i in range(n):
        simMoveStackItemToTop(stack, oldsz - 1)
        read_value_from_stack(stack)
        simMoveStackItemToTop(stack, oldsz - 1)
        l.append(read_value_from_stack(stack))
    return l

def read_table_from_stack(stack):
    from coppeliasim.lib import (
        simGetStackTableInfo,
        sim_stack_table_map,
        sim_stack_table_empty,
    )
    sz = simGetStackTableInfo(stack, 0)
    if sz >= 0:
        return read_list_from_stack(stack)
    elif sz == sim_stack_table_map or sz == sim_stack_table_empty:
        return read_dict_from_stack(stack)

def read_value_from_stack(stack):
    from coppeliasim.lib import (
        simGetStackItemType,
        sim_stackitem_null,
        sim_stackitem_double,
        sim_stackitem_bool,
        sim_stackitem_string,
        sim_stackitem_table,
        sim_stackitem_integer,
    )
    item_type = simGetStackItemType(stack, -1)
    if item_type == sim_stackitem_null:
        value = read_null_from_stack(stack)
    elif item_type == sim_stackitem_double:
        value = read_double_from_stack(stack)
    elif item_type == sim_stackitem_bool:
        value = read_bool_from_stack(stack)
    elif item_type == sim_stackitem_string:
        value = read_string_from_stack(stack)
    elif item_type == sim_stackitem_table:
        value = read_table_from_stack(stack)
    elif item_type == sim_stackitem_integer:
        value = read_long_from_stack(stack)
    else:
        raise RuntimeError(f'unexpected stack item type: {item_type}')
    return value

def read_stack_into_tuple(stack):
    from coppeliasim.lib import (
        simGetStackSize,
        simMoveStackItemToTop,
        simPopStackItem,
    )
    stack_size = simGetStackSize(stack)
    tuple_data = []
    for i in range(stack_size):
        simMoveStackItemToTop(stack, 0)
        tuple_data.append(read_value_from_stack(stack))
    simPopStackItem(stack, 0) # clear all
    return tuple(tuple_data)

def write_null_to_stack(stack, value):
    from coppeliasim.lib import (
        simPushNullOntoStack,
    )
    simPushNullOntoStack(stack)

def write_double_to_stack(stack, value):
    from coppeliasim.lib import (
        simPushDoubleOntoStack,
    )
    simPushDoubleOntoStack(stack, value)

def write_bool_to_stack(stack, value):
    from coppeliasim.lib import (
        simPushBoolOntoStack,
    )
    simPushBoolOntoStack(stack, value)

def write_int_to_stack(stack, value):
    from coppeliasim.lib import (
        simPushInt32OntoStack,
    )
    simPushInt32OntoStack(stack, value)

def write_string_to_stack(stack, value):
    from coppeliasim.lib import (
        simPushStringOntoStack,
    )
    simPushStringOntoStack(stack, value.encode('utf-8'), len(value))

def write_dict_to_stack(stack, value):
    from coppeliasim.lib import (
        simPushTableOntoStack,
        simInsertDataIntoStackTable,
    )
    simPushTableOntoStack(stack)
    for k, v in value.items():
        write_value_to_stack(stack, k)
        write_value_to_stack(stack, v)
        simInsertDataIntoStackTable(stack)

def write_list_to_stack(stack, value):
    from coppeliasim.lib import (
        simPushTableOntoStack,
        simInsertDataIntoStackTable,
    )
    simPushTableOntoStack(stack)
    for i, v in enumerate(value):
        write_value_to_stack(stack, i)
        write_value_to_stack(stack, v)
        simInsertDataIntoStackTable(stack)

def write_value_to_stack(stack, value):
    if value is None:
        write_null_to_stack(stack, value)
    elif isinstance(value, float):
        write_double_to_stack(stack, value)
    elif isinstance(value, bool):
        write_bool_to_stack(stack, value)
    elif isinstance(value, int):
        write_int_to_stack(stack, value)
    elif isinstance(value, str):
        write_string_to_stack(stack, value)
    elif isinstance(value, dict):
        write_dict_to_stack(stack, value)
    elif isinstance(value, list):
        write_list_to_stack(stack, value)
    else:
        raise RuntimeError(f'unexpected type: {type(value)}')

def debug_stack(stack, info = None):
    from coppeliasim.lib import (
        simGetStackSize,
        simDebugStack,
    )
    info = '' if info is None else f' {info} '
    n = (70 - len(info)) // 2
    m = 70 - len(info) - n
    print('#' * n + info + '#' * m)
    for i in range(simGetStackSize(stack)):
        simDebugStack(stack, i)
    print('#' * 70)

def write_tuple_to_stack(stack, tuple_data):
    for item in tuple_data:
        write_value_to_stack(stack, item)

def callback(f):
    def wrapper(stack):
        try:
            inArgs = read_stack_into_tuple(stack)
            outArgs = f(*inArgs)
            if outArgs is None:
                outArgs = ()
            elif not isinstance(outArgs, tuple):
                outArgs = (outArgs,)
            write_tuple_to_stack(stack, outArgs)
            return 1
        except Exception:
            import traceback
            traceback.print_exc()
            return 0
    return wrapper

#def callback_cbor(f):
#    import cbor
#
#    def wrapper(stack):
#        from coppeliasim.lib import (
#            simGetStackStringValue,
#            simReleaseBuffer,
#            simPushStringOntoStack,
#        )
#        try:
#            sz = ctypes.c_int()
#            ptr = simGetStackStringValue(stack, ctypes.byref(sz))
#            o = cbor.loads(ctypes.string_at(ptr, sz.value))
#            o = f(o)
#            simReleaseBuffer(ptr)
#            simPushStringOntoStack(stack, ctypes.c_char_p(cbor.dumps(o)), 0)
#            return 1
#        except Exception:
#            import traceback
#            traceback.print_exc()
#            return 0
#    return wrapper
