# if the library has some @executable_path dependencies, it will fail
# to load; change tose to @rpath via install_name_tool, e.g.:
# install_name_tool -change @executable_path/../Frameworks/libqscintilla2_qt5.13.dylib @rpath/libqscintilla2_qt5.13.dylib libcoppeliaSim.dylib
#
# additionally, need to set DYLD_LIBRARY_PATH=$PWD/../Frameworks
# to avoid other similar load errors

from ctypes import *
import argparse
import threading
import os
import sys

parser = argparse.ArgumentParser(description='CoppeliaSim client.')
parser.add_argument('coppeliaSim_library', type=str, help='Path to the coppeliaSim shared library')
args = parser.parse_args()

coppeliaSimLib = cdll.LoadLibrary(args.coppeliaSim_library)
appDir = os.path.dirname(args.coppeliaSim_library)
coppeliaSimLib.simInitialize(c_char_p(appDir.encode('utf-8')), 0)
while not coppeliaSimLib.simGetExitRequest():
    coppeliaSimLib.simLoop(None, 0)
coppeliaSimLib.simDeinitialize()
