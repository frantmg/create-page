#!/usr/bin/env python3
"""Brand hex -> M3 color roles as CSS custom properties.
Usage: python3 m3_scheme.py "#1463FF" [--variant fidelity|tonal_spot|content|vibrant] > tokens.css"""
import argparse, importlib
from materialyoucolor.hct import Hct
from materialyoucolor.dynamiccolor.material_dynamic_colors import MaterialDynamicColors as M
ROLES=("primary onPrimary primaryContainer onPrimaryContainer secondary onSecondary secondaryContainer "
 "onSecondaryContainer tertiary onTertiary tertiaryContainer onTertiaryContainer error onError errorContainer "
 "onErrorContainer surface onSurface surfaceVariant onSurfaceVariant surfaceContainerLowest surfaceContainerLow "
 "surfaceContainer surfaceContainerHigh surfaceContainerHighest inverseSurface inverseOnSurface inversePrimary "
 "outline outlineVariant scrim").split()
kebab=lambda n:"".join("-"+c.lower() if c.isupper() else c for c in n)
ap=argparse.ArgumentParser(); ap.add_argument("hex"); ap.add_argument("--variant",default="fidelity"); a=ap.parse_args()
mod=importlib.import_module(f"materialyoucolor.scheme.scheme_{a.variant}")
cls=getattr(mod,"Scheme"+"".join(p.title() for p in a.variant.split("_")))
seed=Hct.from_int(0xff000000|int(a.hex.lstrip("#"),16))
def roles(dark):
    s=cls(seed,dark,0.0)
    return "\n".join(f"  --md-sys-color-{kebab(r)}: #{getattr(M,r).get_hct(s).to_int()&0xffffff:06X};" for r in ROLES)
print(f"/* M3 scheme from {a.hex} ({a.variant}) */\n:root {{\n{roles(False)}\n}}\n[data-theme=dark] {{\n{roles(True)}\n}}")
s=cls(seed,False,0.0)
for pal in ("primary","secondary","tertiary","neutral"):
    tones=getattr(s,pal+"_palette")
    print(f"/* {pal} tones: " + "  ".join(f"{t}:#{tones.tone(t)&0xffffff:06X}" for t in (10,20,30,40,50,60,70,80,90,95,98)) + " */")
