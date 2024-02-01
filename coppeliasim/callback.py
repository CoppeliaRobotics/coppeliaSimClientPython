def callback(f):
    def wrapper(stackHandle):
        import coppeliasim.stack as stack

        from typing import get_args, Tuple

        inTypes = tuple(
            [arg_type.__name__ for arg, arg_type in f.__annotations__.items() if arg != 'return']
        )

        if return_annotation := f.__annotations__.get('return'):
            origin = getattr(return_annotation, '__origin__', None)
            if origin in (tuple, list):  # Handling built-in tuple and list
                outTypes = tuple([t.__name__ for t in get_args(return_annotation)])
            elif origin:  # Handling other generic types like Tuple, List from typing
                outTypes = (origin.__name__,)
            else:
                outTypes = (return_annotation.__name__,)
        else:
            outTypes = ()

        try:
            inArgs = stack.read(stackHandle, inTypes)
            outArgs = f(*inArgs)
            if outArgs is None:
                outArgs = ()
            elif not isinstance(outArgs, tuple):
                outArgs = (outArgs,)
            stack.write(stackHandle, outArgs, outTypes)
            return 1
        except Exception:
            import traceback
            traceback.print_exc()
            return 0
    return wrapper
