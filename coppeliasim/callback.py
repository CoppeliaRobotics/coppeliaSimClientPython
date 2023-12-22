import ctypes


def read_stack_into_tuple(stack):
    from coppeliasim.lib import (
        simGetStackSize,
        simMoveStackItemToTop,
        simGetStackItemType,
        simGetStackDoubleValue,
        simGetStackBoolValue,
        simGetStackStringValue,
        simGetStackTableInfo,
        simGetStackInt32Value,
        simPopStackItem,
        sim_stackitem_null,
        sim_stackitem_double,
        sim_stackitem_bool,
        sim_stackitem_string,
        sim_stackitem_table,
        sim_stackitem_func,
        sim_stackitem_userdat,
        sim_stackitem_thread,
        sim_stackitem_lightuserdat,
        sim_stackitem_integer,
        sim_stack_table_circular_ref,
        sim_stack_table_not_table,
        sim_stack_table_map,
        sim_stack_table_empty,
    )
    stack_size = simGetStackSize(stack)
    tuple_data = []
    for i in range(stack_size):
        simMoveStackItemToTop(stack, stack_size - 1 - i)
        item_type = simGetStackItemType(stack, 0)
        if item_type == sim_stackitem_null:
            tuple_data.append(None)
        elif item_type == sim_stackitem_double:
            value = ctypes.c_double()
            simGetStackDoubleValue(stack, ctypes.byref(value))
            tuple_data.append(value.value)
        elif item_type == sim_stackitem_bool:
            value = ctypes.c_bool()
            simGetStackBoolValue(stack, ctypes.byref(value))
            tuple_data.append(value.value)
        elif item_type == sim_stackitem_string:
            string_size = ctypes.c_int()
            string_ptr = simGetStackStringValue(stack, ctypes.byref(string_size))
            string_value = ctypes.string_at(string_ptr, string_size.value)
            tuple_data.append(string_value.decode('utf-8'))
        elif item_type == sim_stackitem_table:
            if simGetStackTableInfo(stack, 0) == sim_stack_table_map:
                # TODO: implement this
                tuple_data.append(dict())
        elif item_type == sim_stackitem_integer:
            value = ctypes.c_int32()
            simGetStackInt32Value(stack, ctypes.byref(value))
            tuple_data.append(value.value)
        simPopStackItem(stack, 1)
    return tuple(tuple_data)

def write_tuple_to_stack(stack, tuple_data):
    from coppeliasim.lib import (
        simPushBoolOntoStack,
        simPushInt32OntoStack,
        simPushStringOntoStack,
        simPushTableOntoStack,
    )
    for item in tuple_data:
        if isinstance(item, bool):
            simPushBoolOntoStack(stack, item)
        elif isinstance(item, int):
            simPushInt32OntoStack(stack, item)
        elif isinstance(item, str):
            simPushStringOntoStack(stack, item.encode('utf-8'), len(item))
        elif isinstance(item, dict):
            simPushTableOntoStack(stack)
            # TODO: implement this

def callback(f):
    def wrapper(stack):
        try:
            inArgs = read_stack_into_tuple(stack)
            outArgs = f(*inArgs)
            write_tuple_to_stack(stack, outArgs)
            return 1
        except Exception as e:
            import traceback
            traceback.print_exc()
            return 0
    return wrapper
