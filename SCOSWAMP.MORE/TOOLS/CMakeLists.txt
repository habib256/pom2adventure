cmake_minimum_required(VERSION 3.16)
project(scoswamp_hgr LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(POM2_SRC "/Users/gistair/src/pom2/src" CACHE PATH "POM2 source directory")
if(NOT EXISTS "${POM2_SRC}/hgrpaint/Cam16.cpp")
    message(FATAL_ERROR "Set POM2_SRC to the POM2 src directory")
endif()

add_executable(scoswamp_hgr
    scoswamp_hgr.cpp
    "${POM2_SRC}/hgrpaint/Cam16.cpp"
)

add_executable(scoswamp_dhgr
    scoswamp_dhgr.cpp
    "${POM2_SRC}/hgrpaint/Cam16.cpp"
    "${POM2_SRC}/hgrpaint/HgrConvert.cpp"
    "${POM2_SRC}/hgrpaint/HgrPaintModel.cpp"
    "${POM2_SRC}/hgrpaint/DhgrNtsc8Palette.cpp"
)
target_include_directories(scoswamp_dhgr PRIVATE
    "${POM2_SRC}"
    "${POM2_SRC}/hgrpaint"
)
target_compile_options(scoswamp_dhgr PRIVATE -Wall -Wextra -Wpedantic
    $<$<NOT:$<CONFIG:Debug>>:-O2>)
target_include_directories(scoswamp_hgr PRIVATE
    "${POM2_SRC}"
    "${POM2_SRC}/hgrpaint"
)
target_compile_options(scoswamp_hgr PRIVATE -Wall -Wextra -Wpedantic)

enable_testing()
add_executable(test_hgr_rle
    test_hgr_rle.c
    ../../SCOSWAMP/SRC/hgr_rle.c
)
target_include_directories(test_hgr_rle PRIVATE ../../SCOSWAMP/SRC)
target_compile_options(test_hgr_rle PRIVATE -Wall -Wextra -Wpedantic)
add_test(NAME hgr_rle COMMAND test_hgr_rle)

add_executable(test_rules
    test_rules.c
    ../../SCOSWAMP/SRC/rules.c
    ../../SCOSWAMP/SRC/dice.c
)
target_include_directories(test_rules PRIVATE ../../SCOSWAMP/SRC)
target_compile_options(test_rules PRIVATE -Wall -Wextra -Wpedantic)
add_test(NAME rules COMMAND test_rules)

add_executable(build_prodos_volume
    build_prodos_volume.cpp
    "${POM2_SRC}/ProDOSVolume.cpp"
)
target_include_directories(build_prodos_volume PRIVATE "${POM2_SRC}")
