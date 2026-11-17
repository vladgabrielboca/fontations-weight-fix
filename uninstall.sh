#!/bin/bash
# Remove everything install.sh added and go back to the stock fonts.
set -eu
rm -rf ~/.local/share/fonts/inter ~/.local/share/fonts/adwaita-heavy ~/.local/share/inter-weights
rm -f ~/.config/fontconfig/conf.d/74-adwaita-heavy.conf ~/.local/bin/inter-weight
fc-cache -f >/dev/null
echo "Removed. Restart Chromium, Electron and GTK apps."
