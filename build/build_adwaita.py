"""Build a static Adwaita Sans family with heavier Regular/Italic.

usage: build_adwaita.py <system Adwaita dir> <store dir> <weight> [<weight> ...]

Adwaita Sans (GNOME's UI font, which GTK and the Chromium UI use) ships as one
variable file per slant. We can't put a heavier static Regular next to the stock
variable file: its named instances carry an opsz size range (14-32), fontconfig
penalises them at 11pt, and Bold requests then fall back to the static Regular.
So we build the whole family as static files:
  <store>/adwaita-static/   every named instance except Regular/Italic, stock coordinates
  <store>/<weight>/         Regular + Italic at the heavier wght, still named Regular/Italic
"""
import os
import sys

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

src_dir, store, weights = sys.argv[1], sys.argv[2], [int(w) for w in sys.argv[3:]]
SRC = {"AdwaitaSans-Regular.ttf": False, "AdwaitaSans-Italic.ttf": True}
RIBBI = ("Regular", "Italic", "Bold", "Bold Italic")


def finish(f, style, wclass, italic, path):
    n = f["name"]
    for nid in (16, 17, 21, 22, 25):
        n.removeNames(nameID=nid)
    family = "Adwaita Sans" if style in RIBBI else "Adwaita Sans " + style.replace(" Italic", "")
    sub = style if style in RIBBI else ("Italic" if italic else "Regular")
    for nid, s in ((1, family), (2, sub), (4, "Adwaita Sans " + style),
                   (6, "AdwaitaSans-" + style.replace(" ", "")), (16, "Adwaita Sans"), (17, style)):
        n.setName(s, nid, 3, 1, 0x409)
    os2 = f["OS/2"]
    os2.usWeightClass = wclass
    bold = style in ("Bold", "Bold Italic")
    os2.fsSelection = ((os2.fsSelection & ~0b1100001) | (1 if italic else 0)
                       | (0b100000 if bold else 0) | (0b1000000 if not italic and not bold else 0))
    f["head"].macStyle = (1 if bold else 0) | (2 if italic else 0)
    if "STAT" in f:
        del f["STAT"]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    f.save(path)


static_dir = os.path.join(store, "adwaita-static")
if not os.path.isdir(static_dir):
    for src, italic in SRC.items():
        vf = TTFont(os.path.join(src_dir, src))
        for inst in vf["fvar"].instances:
            style = vf["name"].getDebugName(inst.subfamilyNameID)
            if style in ("Regular", "Italic"):
                continue
            loc = dict(inst.coordinates)
            loc["opsz"] = 14
            f = instantiateVariableFont(TTFont(os.path.join(src_dir, src)), loc)
            finish(f, style, int(loc["wght"]), italic,
                   os.path.join(static_dir, f"AdwaitaSans-{style.replace(' ', '')}.ttf"))
            print(f"  Adwaita static {style}")

for w in weights:
    for src, italic in SRC.items():
        f = instantiateVariableFont(TTFont(os.path.join(src_dir, src)), {"wght": w, "opsz": 14})
        style = "Italic" if italic else "Regular"
        finish(f, style, 400, italic, os.path.join(store, str(w), src))
        print(f"  Adwaita {w} {style}")
