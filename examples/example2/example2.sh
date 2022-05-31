#!/bin/sh
latex --shell-escape example2.tex
dvips example2.dvi
ps2pdf example2.ps
