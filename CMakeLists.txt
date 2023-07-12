cmake_minimum_required(VERSION 3.20)
project(coppeliaSimClientApplication)

set(CMAKE_CXX_STANDARD 17)

add_definitions(-DQT_FRAMEWORK)
find_package(Qt5 COMPONENTS Core REQUIRED)

if(NOT COPPELIASIM_INCLUDE_DIR)
    if(DEFINED ENV{COPPELIASIM_ROOT_DIR})
        set(COPPELIASIM_INCLUDE_DIR $ENV{COPPELIASIM_ROOT_DIR}/programming/include)
    else()
        set(COPPELIASIM_INCLUDE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../include)
    endif()
endif()

include_directories("${COPPELIASIM_INCLUDE_DIR}")

if(WIN32)
    add_definitions(-DWIN_SIM)
elseif(APPLE)
    add_definitions(-DMAC_SIM)
elseif(UNIX)
    add_definitions(-DLIN_SIM)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread")
endif()

add_executable(main_with_ui main_with_ui.cpp "${COPPELIASIM_INCLUDE_DIR}/simLib/simLib.cpp")
target_link_libraries(main_with_ui Qt5::Core)
