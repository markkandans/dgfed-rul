"""Render LaTeX math and native TikZ diagrams to transparent 300-dpi PNGs.

Used by build_pptx.py so the PowerPoint deck shows the SAME equations and block
diagrams as the Beamer deck (many use \\underbrace / \\xrightarrow / cases that
matplotlib mathtext cannot render). Requires pdflatex + ImageMagick (magick/convert).
"""
import os, subprocess, tempfile, shutil, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "figures")
TIKZDIR = os.path.join(HERE, "..", "beamer", "tikz")
os.makedirs(OUTDIR, exist_ok=True)

# palette mirrors beamer/main.tex + figures/talk_style.py
PREAMBLE = r"""
\documentclass[border=3pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb,bm}
\usepackage{xcolor}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,positioning,calc,fit,shapes.geometric}
\definecolor{accent}{HTML}{0F7173}
\definecolor{cblue}{HTML}{2A78D6}
\definecolor{corange}{HTML}{EB6834}
\definecolor{caqua}{HTML}{1BAF7A}
\definecolor{cyellow}{HTML}{EDA100}
\definecolor{cmagenta}{HTML}{E87BA4}
\newcommand{\alert}[1]{\textcolor{accent}{#1}}
\newcommand{\antsym}{\tikz[baseline=-0.5mm]{\draw[thick]
  (0,-1.6mm) -- (0,1.0mm) (0,1.0mm) -- (-1.5mm,3.2mm)
  (0,1.0mm) -- (1.5mm,3.2mm) (-1.5mm,3.2mm) -- (1.5mm,3.2mm);}}
\tikzset{
  blk/.style={draw=accent, thick, rounded corners=2pt, align=center,
              minimum height=8.5mm, minimum width=16mm, font=\footnotesize,
              fill=accent!8},
  blkb/.style={blk, draw=cblue, fill=cblue!8},
  arr/.style={-{Latex[length=2.6mm]}, thick},
  lab/.style={font=\scriptsize, inner sep=1pt, align=center},
}
"""

_MAGICK = shutil.which("magick")
_CONVERT = shutil.which("convert")


def _pdf_to_png(pdf, png, dpi):
    """PDF -> trimmed transparent PNG via ImageMagick."""
    args = ["-density", str(dpi), pdf, "-trim", "+repage",
            "-background", "none", "-alpha", "on", png]
    if _MAGICK:
        subprocess.run([_MAGICK] + args, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.run([_CONVERT] + args, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _compile(body, name, dpi):
    out_png = os.path.join(OUTDIR, name + ".png")
    with tempfile.TemporaryDirectory() as td:
        tex = os.path.join(td, "s.tex")
        with open(tex, "w") as f:
            f.write(PREAMBLE + "\\begin{document}\n" + body + "\n\\end{document}\n")
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                            "s.tex"], cwd=td, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
        pdf = os.path.join(td, "s.pdf")
        if not os.path.exists(pdf):
            log = r.stdout.decode("utf-8", "replace")
            raise RuntimeError(f"pdflatex failed for {name}:\n{log[-1500:]}")
        _pdf_to_png(pdf, out_png, dpi)
    return out_png


def eq(latex, name=None, dpi=340):
    """Render display-style math (standalone dislikes \\[...\\], so use $\\displaystyle$)."""
    if name is None:
        name = "eq_" + hashlib.md5(latex.encode()).hexdigest()[:10]
    return _compile("$\\displaystyle " + latex + "$", name, dpi)


def tikz(tikz_filename, name=None, dpi=300):
    """Render one of beamer/tikz/*.tex (native TikZ) to PNG."""
    path = os.path.join(TIKZDIR, tikz_filename)
    with open(path) as f:
        body = f.read()
    if name is None:
        name = os.path.splitext(tikz_filename)[0]
    return _compile(body, name, dpi)


if __name__ == "__main__":
    # smoke test: one hard equation (underbrace) + one tikz diagram
    print(eq(r"\mathrm{PL}(f,d)="
             r"\underbrace{\left(\tfrac{4\pi f d}{c}\right)^{2}}_{\text{spreading}}"
             r"\cdot\underbrace{e^{\kappa_{\mathrm{abs}}(f)\,d}}_{\text{molecular abs.}}",
             "eq_thz_pl"))
    print(tikz("otfs_chain.tex"))
    print("latex_render smoke test OK")
