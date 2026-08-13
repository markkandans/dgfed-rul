"""Fig. 1 v2 - global 3-row grid across both containers; all arrows single
continuous patches; Okabe-Ito-adjacent palette, grayscale-safe via weights."""
import os

import matplotlib
matplotlib.use("Agg")

FIGDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "latex", "figures")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.path import Path

SLATE="#33475B"; INK="#1A1A1A"; GRAY="#6B7A89"
ORANGE="#D95F02"; TINT_O="#FDEAD7"; TINT_B="#DCE9F7"
CL_BG="#EDF3FA"; SV_BG="#F4EFE7"; EDGE="#8A97A5"

fig, ax = plt.subplots(figsize=(7.16, 2.45))
ax.set_xlim(0,100); ax.set_ylim(0,33); ax.axis("off")

def box(x,y,w,h,text,fc="#FFFFFF",fs=8.0,lw=1.1):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.22",
                 fc=fc,ec=SLATE,lw=lw,zorder=3,mutation_scale=1.0))
    ax.text(x+w/2,y+h/2,text,ha="center",va="center",fontsize=fs,zorder=4)

def arrow(p,q,color=SLATE,lw=1.4,ls="-",ms=11):
    ax.add_patch(FancyArrowPatch(p,q,arrowstyle="-|>",color=color,lw=lw,
                 linestyle=ls,mutation_scale=ms,shrinkA=0,shrinkB=0,zorder=2))

def elbow(pts,color=SLATE,lw=1.4,ls="-",ms=11):
    ax.add_patch(FancyArrowPatch(path=Path(pts),arrowstyle="-|>",color=color,
                 lw=lw,linestyle=ls,mutation_scale=ms,shrinkA=0,shrinkB=0,zorder=2))

def note(x,y,t,fs=7.2,color="#222222",frame=False):
    bb = dict(fc="white",ec=ORANGE if frame else "none",lw=0.8,pad=1.8) if frame \
         else dict(fc="white",ec="none",pad=0.8)
    ax.text(x,y,t,ha="center",va="center",fontsize=fs,color=color,zorder=5,bbox=bb)

# containers + titles
ax.add_patch(FancyBboxPatch((1,1),55,30,boxstyle="round,pad=0.3",fc=CL_BG,ec=EDGE,lw=1.3,zorder=0))
ax.add_patch(FancyBboxPatch((59.5,1),39.5,30,boxstyle="round,pad=0.3",fc=SV_BG,ec=EDGE,lw=1.3,zorder=0))
ax.text(3,29.8,"Edge client $k$",fontsize=9,fontweight="bold",style="italic",color="#2B3A49",zorder=4)
ax.text(61.3,29.8,"Server",fontsize=9,fontweight="bold",style="italic",color="#2B3A49",zorder=4)

# ROW 1 (y 20.5-26.5)
box(3,20.5,13,6,"Sensor stream\n(non-stationary)")
box(18.5,20.5,17,6,"Local training, $E$ epochs\n(full model federated)",fs=7.6)
box(39,20.5,14,6,"Page\u2013Hinkley\ndetector  (2)\u2013(3)",fc=TINT_O)
box(75.5,20.5,14,6,"Global model $\\theta$",fc=TINT_B)
# ROW 2 (y 11.5-17.5)
box(35,11.5,18,6,"Event trigger  (4)\nskip iff $d_k{=}0 \\wedge \\|\\Delta_k\\|{<}\\gamma H_k$",fc=TINT_O,fs=7.2)
box(72,11.5,19,6,"Staleness/drift-aware\naggregation  (9)\n$w_k{=}\\,n_k\\,\\frac{\\tau_0}{\\tau_0+a_k}\\,\\rho^{\\,d_k}$",fc=TINT_O,fs=7.0)
# ROW 3 (y 2.5-8.5)
box(36,2.5,16,6,"EF top-$k$ + 8-bit\nquantization  (5)\u2013(7)",fs=7.6)
box(63.5,2.5,11,6,"Decompress")
box(77.5,2.5,13,6,"Adaptive clip  (8)\n$c\\cdot\\mathrm{med}\\,\\|\\Delta\\|$",fs=7.4)

# client flow
arrow((16,23.5),(18.5,23.5))
arrow((35.5,23.5),(39,23.5)); note(37.2,27.2,"residuals $r_i$")
arrow((46,20.5),(46,17.5),color=ORANGE,lw=2.4,ms=13); note(44.1,18.9,"$d_k$",fs=8,color=ORANGE)
elbow([(27,20.5),(27,14.5),(35,14.5)]); note(28.8,16.6,"$\\Delta_k$",fs=8)
elbow([(35,12.8),(21,12.8),(21,20.5)],ls=(0,(4,3)),color=GRAY,lw=1.3)
note(27.5,11.2,"skip (stay silent)",color=GRAY)
arrow((44,11.5),(44,8.5)); note(46.4,10.0,"send")
# uplink pipeline (row 3, straight through the boundary)
arrow((52,5.5),(63.5,5.5),color=INK,lw=2.0,ms=13)
note(57.7,7.3,"uplink, $b_k$ bytes",fs=7.0)
note(57.7,3.6,"$(\\tilde{\\Delta}_k, n_k, d_k, a_k)$",fs=6.6)
# server flow
arrow((74.5,5.5),(77.5,5.5))
arrow((84,8.5),(84,11.5))
arrow((82,17.5),(82,20.5)); note(85.0,19.0,"update")
# loop-closing drift signal
elbow([(53,23.5),(60.8,23.5),(60.8,14.5),(72,14.5)],color=ORANGE,lw=2.4,ms=13)
note(68.3,19.6,"one flag $d_k$ governs\nupload and weight",fs=7.0,color=ORANGE,frame=True)
# broadcast lane
elbow([(82.5,26.5),(82.5,28.4),(27,28.4),(27,26.5)],color=GRAY,lw=1.5,ls=(0,(5,3)))
note(54,28.4,"broadcast $\\theta$",color=GRAY)

plt.tight_layout(pad=0.15)
for ext in ("pdf","png"):
    plt.savefig(os.path.join(FIGDIR, f"fig1_loop.{ext}"),dpi=300,bbox_inches="tight")
print("v2 written")
