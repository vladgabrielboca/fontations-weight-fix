#!/bin/bash
# Build heavier Inter (+ Adwaita Sans, if installed) and switch to them.
#   ./install.sh            builds 430 450 475 500, installs 450
#   WEIGHT=475 ./install.sh installs 475 instead
#   WEIGHTS="440 460" ./install.sh builds other weights (100-900 are valid)
set -euo pipefail
cd "$(dirname "$0")"

INTER_VERSION=4.1
INTER_SHA256=9883fdd4a49d4fb66bd8177ba6625ef9a64aa45899767dde3d36aa425756b11e
WEIGHTS=${WEIGHTS:-"430 450 475 500"}
WEIGHT=${WEIGHT:-450}
store=~/.local/share/inter-weights
fonts=~/.local/share/fonts/inter

# fontTools: system package if present, otherwise a throwaway uv environment.
if python3 -c 'import fontTools' 2>/dev/null; then
  py() { python3 "$@"; }
elif command -v uv >/dev/null; then
  py() { uv run --quiet --no-project --with fonttools python "$@"; }
else
  echo "Needs fontTools: install python-fonttools (Arch), python3-fonttools (Debian/Fedora) or uv." >&2
  exit 1
fi

tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
echo "Downloading Inter $INTER_VERSION"
curl -fsSL -o "$tmp/inter.zip" "https://github.com/rsms/inter/releases/download/v$INTER_VERSION/Inter-$INTER_VERSION.zip"
echo "$INTER_SHA256  $tmp/inter.zip" | sha256sum -c --quiet
python3 -c 'import sys, zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])' "$tmp/inter.zip" "$tmp/inter"

# Stock static Inter family (all weights), plus the stock Regular/Italic as weight "400".
mkdir -p "$fonts" "$store/400"
cp "$tmp"/inter/extras/ttf/Inter-*.ttf "$fonts/"
cp "$tmp"/inter/extras/ttf/Inter-{Regular,Italic}.ttf "$store/400/"
cp "$tmp/inter/LICENSE.txt" "$fonts/LICENSE.txt"

echo "Building Inter weights: $WEIGHTS"
py build/build_inter.py "$tmp/inter" "$store" $WEIGHTS

# Adwaita Sans: GNOME's UI font, used by GTK and by Chromium's own tabs/omnibox.
# Look on disk first: once the fix is active, fontconfig hides the stock files.
adwfile=$({ find /usr/share/fonts /usr/local/share/fonts -name AdwaitaSans-Regular.ttf 2>/dev/null
            fc-list --format '%{file}\n' 'Adwaita Sans'; } |
          grep '/AdwaitaSans-Regular.ttf$' | grep -v -e "^$HOME/" -e '/adwaita-heavy/' | head -n1 || true)
if [ -n "$adwfile" ]; then
  adwsrc=$(dirname "$adwfile")
  echo "Building Adwaita Sans weights from $adwsrc"
  rm -rf "$store/adwaita-static"
  py build/build_adwaita.py "$adwsrc" "$store" $WEIGHTS
  echo "$adwsrc" > "$store/adwaita-src-dir"
else
  echo "No system Adwaita Sans found, skipping it."
  rm -f "$store/adwaita-src-dir"
fi

mkdir -p ~/.local/bin
install -m 755 bin/inter-weight ~/.local/bin/inter-weight
~/.local/bin/inter-weight "$WEIGHT"
