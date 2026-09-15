#!/bin/sh
set -eu
tools_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
pom2_root=${POM2_ROOT:-"$tools_dir/../../../pom2"}
pom2_root=$(CDPATH= cd -- "$pom2_root" && pwd)
mkdir -p "$tools_dir/build"
c++ -std=c++17 -O2 -DNDEBUG -I"$pom2_root/src" -I"$pom2_root/include" \
    -I"$pom2_root/build/generated" -I"$pom2_root/imgui" \
    -DPOM2_ROOT=\""$pom2_root"\" "$tools_dir/pom2_playtest.cpp" \
    "$pom2_root/build/libpom2_core.a" \
    -framework CoreAudio -framework AudioToolbox -framework AudioUnit \
    -o "$tools_dir/build/pom2_playtest"
