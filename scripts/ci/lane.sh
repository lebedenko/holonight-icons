#!/bin/sh
set -eu
lane=$1
mkdir /work/source
cp -a /input/. /work/source/
cd /work/source
export HOME=/work/build/home LC_ALL=C.UTF-8 TZ=UTC
mkdir -p "$HOME"
if [ "$lane" = licensing ]; then
  python3 --version
  python3 scripts/build.py
  reuse --version
  reuse lint
  reuse --root build/HoloNight lint
  reuse --root build/HoloNight-Dark lint
  reuse --root build/holonight-icons lint
  exit
fi
[ "$lane" = verification ] || exit 2
python3 --version
git --version
cmake --version
c++ --version
pkg-config --modversion Qt6Core Qt6Gui Qt6Svg
python3 scripts/ci/test_launcher.py
export PATH="/work/source/scripts/ci:/work/tools/usr/bin:$PATH"
export LD_LIBRARY_PATH=/work/tools/usr/lib
export PYTHONPATH=/work/tools/usr/lib/python3.14/site-packages
export GI_TYPELIB_PATH=/work/tools/usr/lib/girepository-1.0
export XDG_DATA_DIRS=/work/tools/usr/share:/usr/share
export XDG_RUNTIME_DIR=/work/runtime GDK_BACKEND=x11 GSK_RENDERER=cairo GTK_A11Y=none
mkdir -m 700 "$XDG_RUNTIME_DIR"
export GDK_PIXBUF_MODULE_FILE="$XDG_RUNTIME_DIR/loaders.cache"
/work/tools/usr/bin/gdk-pixbuf-query-loaders /work/tools/usr/lib/gdk-pixbuf-2.0/2.10.0/loaders/*.so > "$GDK_PIXBUF_MODULE_FILE"
python3 -c 'import gi; print("PyGObject", gi.__version__)'
python3 -c 'import gi; gi.require_version("Gtk", "3.0"); from gi.repository import Gtk; print("GTK", Gtk.get_major_version(), Gtk.get_minor_version(), Gtk.get_micro_version())'
python3 -c 'import gi; gi.require_version("Gtk", "4.0"); from gi.repository import Gtk; print("GTK", Gtk.get_major_version(), Gtk.get_minor_version(), Gtk.get_micro_version())'
python3 -c 'from pathlib import Path; text=Path("/work/runtime/loaders.cache").read_text(); assert "image/svg+xml" in text, "Missing SVG pixbuf loader"'
python3 -c 'import gi; gi.require_version("GdkPixbuf", "2.0"); from gi.repository import GdkPixbuf; assert any(format.get_name() == "png" for format in GdkPixbuf.Pixbuf.get_formats()), "Missing PNG pixbuf support"'
xvfb-run -a /bin/true
mkdir -p /work/providers
export HOLONIGHT_QT_SOURCE=/work/providers/holonight-qt
revision=7c4fe3c9df0b9a15ed68ddad70b8d05a7312be1a
git init -q "$HOLONIGHT_QT_SOURCE"
git -C "$HOLONIGHT_QT_SOURCE" fetch --depth 1 https://github.com/lebedenko/holonight-qt.git "$revision"
git -C "$HOLONIGHT_QT_SOURCE" checkout --detach FETCH_HEAD
[ "$(git -C "$HOLONIGHT_QT_SOURCE" rev-parse HEAD)" = "$revision" ]
python3 scripts/build.py
python3 scripts/validate_icons.py
python3 -m unittest discover -s tests -v
sh scripts/check-rendering.sh
python3 scripts/check-gtk-symbolic.py
python3 scripts/generate_icon_previews.py
cp -a build/HoloNight build/HoloNight-Dark build/holonight-icons build/previews /output/
