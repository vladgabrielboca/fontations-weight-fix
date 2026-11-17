# fontations-weight-fix

Heavier Inter and Adwaita Sans for Linux, for anyone who found text in
Chrome/Chromium and Electron apps thin and pale after Chromium stopped using
FreeType, and who has no renderer setting left that brings the old look back.

The fix changes the font files rather than the renderer, so it works in every
app: Chromium (Fontations), Firefox, GTK and Qt (FreeType).

## The problem

From Chrome 136 on, Chromium on Linux renders system fonts with
[Fontations](https://github.com/googlefonts/fontations) (Skrifa, a Rust font
stack) instead of FreeType. That's a memory-safety change
([why Chrome replaced FreeType](https://developer.chrome.com/blog/memory-safety-fonts#why_replace_freetype),
[crbug 349952802](https://crbug.com/349952802)), and it means FreeType-only
tuning no longer reaches Chromium:

- `FREETYPE_PROPERTIES` in `/etc/environment` (stem darkening
  `cff:no-stem-darkening=0 autofitter:no-stem-darkening=0`, or
  `truetype:interpreter-version=35`) still works in Firefox, GTK, Qt and
  terminals, but Chromium ignores it.
- The escape hatch `--disable-features=FontationsLinuxSystemFonts` was
  removed after Chrome 139.0.7258, and Chromium does not plan to keep FreeType
  support
  ([maintainer comment](https://github.com/googlefonts/fontations/pull/1496#issuecomment-3004330901)).
- Skrifa doesn't have FreeType's v35 hinting interpreter yet.
  [fontations#1496](https://github.com/googlefonts/fontations/pull/1496) adds
  it and makes rendering look almost the same as FreeType, but the PR has been
  open since May 2025 (see also
  [fontations#1215](https://github.com/googlefonts/fontations/issues/1215)).

So on a normal ~110 PPI monitor, Chromium text is lighter than the same text
in Firefox, and no flag or environment variable can make it heavier.

## The fix

Inter and Adwaita Sans are variable fonts with a weight axis. `install.sh`
cuts static instances at a slightly heavier weight (430 to 500, with 450 as
the default; Regular is 400 and Medium is 500) and installs them under the
**Regular** and **Italic** names. Every app that asks for "Inter Regular" gets
the heavier outlines, whichever rasterizer it uses. Medium, Bold and the other
weights stay stock, so bold text still stands out.

- **Inter**: the static Inter 4.1 family, with Regular/Italic replaced. It
  covers web pages and apps whose sans-serif font resolves to Inter (check with
  `fc-match sans-serif`).
- **Adwaita Sans**: GNOME's UI font (based on Inter), used by GTK apps and by
  Chromium's own tabs and address bar. It ships as one variable file per
  slant, and a static heavier Regular can't sit beside it: the variable named
  instances carry an optical-size range that fontconfig penalises at 11 pt,
  so Bold requests fall back to the Regular. The installer therefore builds the
  whole family as static files and hides the stock variable files with a
  fontconfig `rejectfont` rule (`74-adwaita-heavy.conf`). It's skipped when
  Adwaita Sans isn't installed.

Sites that ship their own web fonts aren't affected. This only changes local
system fonts.

## Install

Requirements: fontconfig, curl, and Python with
[fontTools](https://github.com/fonttools/fonttools) (`python-fonttools` on
Arch, `python3-fonttools` on Debian/Fedora). If fontTools is missing,
[uv](https://docs.astral.sh/uv/) is used instead.

```sh
git clone https://github.com/vladgabrielboca/fontations-weight-fix
cd fontations-weight-fix
./install.sh                 # builds 430 450 475 500, switches to 450
WEIGHT=475 ./install.sh      # switch to another weight
WEIGHTS="440 460" ./install.sh   # build other weights
```

The installer downloads Inter 4.1 from its GitHub release (checking its
SHA-256), builds into `~/.local/share/inter-weights`, installs into
`~/.local/share/fonts/{inter,adwaita-heavy}`, and puts the `inter-weight`
command into `~/.local/bin`.

Fully restart Chromium, Electron apps and GTK apps afterwards. Closing one
window isn't enough.

## Switching weights

```sh
inter-weight          # show what's installed
inter-weight 475      # heavier
inter-weight 400      # stock Inter, stock variable Adwaita Sans
```

## Uninstall

```sh
./uninstall.sh
```

This removes the fonts, the build store, the fontconfig rule and the command.

## License

The scripts are MIT. Inter and Adwaita Sans are under the SIL Open Font
License 1.1. The repo contains no font files; they're downloaded or read from
your system and built on your machine.
