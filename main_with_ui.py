# if the library has some @executable_path dependencies, it will fail
# to load; change tose to @rpath via install_name_tool, e.g.:
# install_name_tool -change @executable_path/../Frameworks/libqscintilla2_qt5.13.dylib @rpath/libqscintilla2_qt5.13.dylib libcoppeliaSim.dylib
#
# additionally, need to set DYLD_LIBRARY_PATH=$PWD/../Frameworks
# to avoid other similar load errors

from ctypes import *
import threading
import os

def simThreadFunc():
    appDir = os.getcwd()
    coppeliaSimLib.simInitialize(appDir, 0)
    while not coppeliaSimLib.simGetExitRequest():
        coppeliaSimLib.simLoop(None, 0)
    coppeliaSimLib.simDeinitialize()

coppeliaSimLib = cdll.LoadLibrary('libcoppeliaSim.dylib')

t = threading.Thread(target=simThreadFunc)
t.start()
options = 0x0ffff # sim_gui_all
coppeliaSimLib.simRunGui(options)
t.join()
