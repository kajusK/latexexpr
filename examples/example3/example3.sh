#!/bin/sh
latex --shell-escape example3.tex
dvips example3.dvi
ps2pdf example3.ps
