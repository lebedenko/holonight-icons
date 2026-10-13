#!/bin/sh
set -eu
lane=$1
mkdir /work/source
cp -a /input/. /work/source/
cd /work/source
export HOME=/work/build/home LC_ALL=C.UTF-8 TZ=UTC
export XDG_DATA_HOME=/work/data XDG_CONFIG_HOME=/work/config XDG_CACHE_HOME=/work/cache
export XDG_RUNTIME_DIR=/work/runtime GDK_BACKEND=x11 GSK_RENDERER=cairo GTK_A11Y=none
mkdir -p "$HOME" "$XDG_DATA_HOME" "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME"
mkdir -m 700 "$XDG_RUNTIME_DIR"
python3 --version
if [ "$lane" = licensing ]; then
  python3 scripts/build.py
  reuse --version
  reuse --no-multiprocessing lint
  reuse --no-multiprocessing --root build/HoloNight lint
  reuse --no-multiprocessing --root build/HoloNight-Dark lint
  reuse --no-multiprocessing --root build/holonight-icons lint
  exit
fi
export VERIFY_RENDERERS=ON
export VERIFY_KDE=${VERIFY_KDE:-OFF}
if [ "$lane" = prepare ]; then
  export HOLONIGHT_QT_SOURCE=/prepared/qt
  task deps
  if [ -d /prepared/deps ]; then
    number=1
    while [ -e "/prepared/deps.previous-$number" ]; do number=$((number + 1)); done
    mv /prepared/deps "/prepared/deps.previous-$number"
  fi
  cp -a build/deps /prepared/deps
  pacman -Q > /prepared/packages.txt
  c++ --version > /prepared/compiler.txt
  cmake --version > /prepared/cmake.txt
  pkg-config --modversion Qt6Core Qt6Gui Qt6Svg gtk+-3.0 gtk4 > /prepared/versions.txt
  exit
fi
mkdir -p build
cp -a /prepared/deps build/deps
cat /prepared/compiler.txt /prepared/cmake.txt /prepared/versions.txt
cp /prepared/packages.txt /prepared/compiler.txt /prepared/cmake.txt /prepared/versions.txt /output/
case "$lane" in
  verification)
    python3 scripts/ci/test_launcher.py
    python3 scripts/ci/test_dependencies.py
    python3 -m unittest discover -s tests -v
    task validate
    task test:render
    task test:gtk
    task preview:icons
    cp -a build/HoloNight build/HoloNight-Dark build/holonight-icons build/previews /output/
    ;;
  minimal)
    export VERIFY_RENDERERS=OFF VERIFY_KDE=OFF
    python3 scripts/dependencies.py check
    task validate
    python3 -m unittest discover -s tests -v
    ;;
  release)
    export VERIFY_RENDERERS=OFF VERIFY_KDE=OFF
    python3 scripts/dependencies.py check
    python3 scripts/stage.py --destdir /work/package
    python3 -c 'from pathlib import Path; paths=list(Path("/work/package").rglob("*")); assert not any(p.suffix in {".o", ".a", ".so", ".cpp", ".h"} or p.name in {"render-check", "kde-check", "CMakeCache.txt"} for p in paths)'
    cp -a /work/package /output/
    ;;
  static)
    task format-check
    cmake -S tests/rendering -B build/rendering -DHOLONIGHT_RENDERER_FIXTURE=/work/source/build/deps/renderer
    cmake --build build/rendering --parallel "${JOBS:-2}"
    python3 scripts/check-static.py
    if [ "$VERIFY_KDE" = ON ]; then
      cmake -S tests/kde -B build/kde
      cmake --build build/kde --parallel "${JOBS:-2}"
      python3 scripts/check-static.py --kde --build build/kde
      task test:kde
    fi
    ;;
  *) exit 2 ;;
esac
