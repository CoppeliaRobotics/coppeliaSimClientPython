cmake_minimum_required(VERSION 3.20)
project(coppeliaSimClientApplication)

set(CMAKE_CXX_STANDARD 17)

add_definitions(-DQT_FRAMEWORK)
set(Qt Qt5 CACHE STRING "Qt version to use (e.g. Qt5)")
set_property(CACHE Qt PROPERTY STRINGS Qt5 Qt6)
find_package(${Qt} COMPONENTS Core REQUIRED)

if(NOT COPPELIASIM_INCLUDE_DIR)
    if(DEFINED ENV{COPPELIASIM_ROOT_DIR})
        set(COPPELIASIM_INCLUDE_DIR $ENV{COPPELIASIM_ROOT_DIR}/programming/include)
    else()
        set(COPPELIASIM_INCLUDE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../include)
    endif()
endif()
list(APPEND CMAKE_MODULE_PATH ${COPPELIASIM_INCLUDE_DIR}/cmake)
find_package(CoppeliaSim 4.6.0.0 REQUIRED)

include_directories("${COPPELIASIM_INCLUDE_DIR}")

if(WIN32)
    add_definitions(-DWIN_SIM)
elseif(APPLE)
    add_definitions(-DMAC_SIM)
elseif(UNIX)
    add_definitions(-DLIN_SIM)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread")
endif()

coppeliasim_add_resource(coppeliaSim.py)
coppeliasim_add_python_directory(coppeliasim)
