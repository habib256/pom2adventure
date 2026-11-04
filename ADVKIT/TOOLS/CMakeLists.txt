cmake_minimum_required(VERSION 3.16)
project(advkit LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

option(ADVKIT_BUILD_TOOLS "Build converters and ProDOS tools" ON)
# Deux origines pour les convertisseurs : le paquet installe de POM2
# (`-DPOM2_SDK_PREFIX=/chemin`, cf. docs/SDK.md de POM2), ou ses sources. Le
# paquet se suffit a lui-meme ; build_prodos_volume, qui n'en fait pas partie,
# a encore besoin des sources et n'est construit que si elles sont la.
set(POM2_SDK_PREFIX "" CACHE PATH "Prefixe d'installation du paquet pom2_imageconv")
set(POM2_SRC "${CMAKE_CURRENT_SOURCE_DIR}/../../../pom2/src" CACHE PATH "POM2 source directory")
if(ADVKIT_BUILD_TOOLS)
add_executable(scoswamp_hgr scoswamp_hgr.cpp)
add_executable(scoswamp_dhgr scoswamp_dhgr.cpp)
if(POM2_SDK_PREFIX)
    find_package(pom2_imageconv CONFIG REQUIRED PATHS "${POM2_SDK_PREFIX}" NO_DEFAULT_PATH)
    target_link_libraries(scoswamp_hgr PRIVATE POM2::imageconv)
    target_link_libraries(scoswamp_dhgr PRIVATE POM2::imageconv)
else()
    if(NOT EXISTS "${POM2_SRC}/hgrpaint/Cam16.cpp")
        message(FATAL_ERROR "Set POM2_SRC to the POM2 src directory, or POM2_SDK_PREFIX to its package")
    endif()
    target_sources(scoswamp_hgr PRIVATE "${POM2_SRC}/hgrpaint/Cam16.cpp")
    target_sources(scoswamp_dhgr PRIVATE
        "${POM2_SRC}/hgrpaint/Cam16.cpp"
        "${POM2_SRC}/hgrpaint/HgrConvert.cpp"
        "${POM2_SRC}/hgrpaint/HgrPaintModel.cpp"
        "${POM2_SRC}/hgrpaint/DhgrNtsc8Palette.cpp"
    )
    foreach(_tool scoswamp_hgr scoswamp_dhgr)
        target_include_directories(${_tool} PRIVATE "${POM2_SRC}" "${POM2_SRC}/hgrpaint")
    endforeach()
endif()
target_compile_options(scoswamp_dhgr PRIVATE -Wall -Wextra -Wpedantic
    $<$<NOT:$<CONFIG:Debug>>:-O2>)
target_compile_options(scoswamp_hgr PRIVATE -Wall -Wextra -Wpedantic)

if(EXISTS "${POM2_SRC}/ProDOSVolume.cpp")
    add_executable(build_prodos_volume
        build_prodos_volume.cpp
        "${POM2_SRC}/ProDOSVolume.cpp"
    )
    target_include_directories(build_prodos_volume PRIVATE "${POM2_SRC}")
elseif(NOT POM2_SDK_PREFIX)
    message(FATAL_ERROR "Set POM2_SRC to the POM2 src directory")
endif()
endif()

enable_testing()
add_executable(test_hgr_rle
    ../../SCOSWAMP.MORE/TOOLS/test_hgr_rle.c
    ../../SCOSWAMP/SRC/hgr_rle.c
)
target_include_directories(test_hgr_rle PRIVATE ../../SCOSWAMP/SRC)
target_compile_options(test_hgr_rle PRIVATE -Wall -Wextra -Wpedantic)
add_test(NAME hgr_rle COMMAND test_hgr_rle)

add_executable(test_rules
    ../../SCOSWAMP.MORE/TOOLS/test_rules.c
    ../../SCOSWAMP/SRC/rules.c
    ../../SCOSWAMP/SRC/dice.c
)
target_include_directories(test_rules PRIVATE ../../SCOSWAMP/SRC)
target_compile_options(test_rules PRIVATE -Wall -Wextra -Wpedantic)
add_test(NAME rules COMMAND test_rules)

add_executable(test_spacetrip_parse ../../SPACETRIP/test_parse.c)
target_compile_options(test_spacetrip_parse PRIVATE -Wall -Wextra -Wpedantic)
add_test(NAME spacetrip_parse COMMAND test_spacetrip_parse)
