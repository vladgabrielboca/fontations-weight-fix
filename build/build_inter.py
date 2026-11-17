"""Build heavier Inter Regular/Italic faces from InterVariable.

usage: build_inter.py <Inter release dir> <store dir> <weight> [<weight> ...]

<Inter release dir> is the unzipped Inter-4.x.zip (InterVariable*.ttf + extras/ttf/).
Writes <store>/<weight>/Inter-{Regular,Italic}.ttf. Each one is the variable font
instanced at wght=<weight>, opsz=14, then given the name table and style bits of
the stock static Regular/Italic, so every app still sees it as "Inter Regular".
"""
import os
import sys

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

src, store, weights = sys.argv[1], sys.argv[2], [int(w) for w in sys.argv[3:]]
pairs = (("InterVariable.ttf", "Inter-Regular.ttf"), ("InterVariable-Italic.ttf", "Inter-Italic.ttf"))

for w in weights:
    out_dir = os.path.join(store, str(w))
    os.makedirs(out_dir, exist_ok=True)
    for var, static in pairs:
        inst = instantiateVariableFont(TTFont(os.path.join(src, var)), {"wght": w, "opsz": 14})
        orig = TTFont(os.path.join(src, "extras", "ttf", static))
        inst["name"] = orig["name"]
        for k in ("usWeightClass", "fsSelection", "achVendID"):
            setattr(inst["OS/2"], k, getattr(orig["OS/2"], k))
        inst["head"].macStyle = orig["head"].macStyle
        if "STAT" in inst:
            del inst["STAT"]
        inst.save(os.path.join(out_dir, static))
        print(f"  Inter {w} {static}")
