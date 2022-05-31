#!/bin/sh
python example1.py > example1.py.tex
latex example1.tex
dvips example1.dvi
ps2pdf example1.ps
