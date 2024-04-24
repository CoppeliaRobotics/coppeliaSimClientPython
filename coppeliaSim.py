import argparse


# refer to the manual (en/coppeliaSimLibrary.htm) for customization examples


def simThreadFunc():
    from coppeliasim.lib import (
        appDir,
        simInitialize,
        simLoop,
        simDeinitialize,
        simGetExitRequest,
    )

    simInitialize(appDir().encode('utf-8'), 0)

    while not simGetExitRequest():
        simLoop(None, 0)

    simDeinitialize()


if __name__ == '__main__':
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
