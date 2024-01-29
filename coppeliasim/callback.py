def callback(f):
    def wrapper(stackHandle):
        import coppeliasim.stack as stack
        try:
            inArgs = stack.read(stackHandle)
            outArgs = f(*inArgs)
            if outArgs is None:
                outArgs = ()
            elif not isinstance(outArgs, tuple):
                outArgs = (outArgs,)
            stack.write(stackHandle, outArgs)
            return 1
        except Exception:
            import traceback
            traceback.print_exc()
            return 0
    return wrapper
