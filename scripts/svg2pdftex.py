#!/usr/local/bin/python3

# SVG to PDF + LaTeX conversion tool

# Simulates "Export to PDF+TeX" option in Inkscape.
# Uses either Inkscape (if available), or cairosvg, with the latter
# option ONLY valid for svg files without any svg transforms.
# In Affinity Designer make sure to use "Flatten transforms" option in
# SVG export window. For SVG files not coming from Affinity Designer,
# use some other SVG flattener tool as desired.

import sys
import argparse
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
import shutil
import subprocess

# The path to Inkscape binary executable (may be different on other systems)
INKSCAPE = r"D:\\Tools\\Inkscape\\bin\\inkscape.exe"
# XML namescape for svg elements
ns = {'svg': 'http://www.w3.org/2000/svg'}


def strippx(attr):
    _, e = re.match('\d+', attr).span()
    return attr[:e]

# Remove all <text> elements from the SVG element tree


def remove_text(root):
    text_pattern = './/svg:text'
    # Removing descendant elements deep in the tree is not easy with xml.etree.
    # See https://stackoverflow.com/a/48637857 .
    text_nodes = root.findall(text_pattern, ns)
    while len(text_nodes):
        parent = root.findall(text_pattern+'/..', ns)[0]
        parent.remove(text_nodes[0])
        text_nodes = root.findall(text_pattern, ns)
    return root

# Collects the information about all <text> elements in the SVG tree


def extract_texts(root):
    texts = []
    for text_element in root.findall('.//svg:text', ns):
        s = "".join(text_element.itertext())
        x = strippx(text_element.get('x'))
        y = strippx(text_element.get('y'))
        texts.append({'text': s, 'x': x, 'y': y})
    return texts

# Read the image size from viewBox attribute of the root <svg> element


def extract_size(root):
    v = root.get('viewBox').split(' ')
    return (float(v[2]), float(v[3]))


def generate_pdftex(imagename, width, height, texts):
    ratio = height / width
    pdftex = ""

    pdftex += r'''%% PDF + LaTeX conversion of an SVG file, based on the
%% PDF + LaTeX output extension for Inkscape (Johan Engelen, 2010)
%% Accompanies image file '''

    pdftex += "'" + imagename + "'\n"

    pdftex += r'''%%
%% To include the image in your LaTeX document, write
%%   \input{<filename>.pdf_tex}
%%  instead of
%%   \includegraphics{<filename>.pdf}
%% To scale the image, write
%%   \def\svgwidth{<desired width>}
%%   \input{<filename>.pdf_tex}
%%  instead of
%%   \includegraphics[width=<desired width>]{<filename>.pdf}
%%
%% Images with a different path to the parent latex file can
%% be accessed with the `import' package (which may need to be
%% installed) using
%%   \usepackage{import}
%% in the preamble, and then including the image with
%%   \import{<path to file>}{<filename>.pdf_tex}
%% Alternatively, one can specify
%%   \graphicspath{{<path to file>/}}
%% 
%% For more information, please see info/svg-inkscape on CTAN:
%%   http://tug.ctan.org/tex-archive/info/svg-inkscape
%%
\begingroup%
  \ifx\svgwidth\undefined%
    \setlength{\unitlength}{'''

    pdftex += "{:.2f}".format(width) + 'bp'

    pdftex += r'''}%
  \else%
    \setlength{\unitlength}{\svgwidth}%
  \fi%
  \global\let\svgwidth\undefined%
  \global\let\svgscale\undefined%
'''

    pdftex += r'  \begin{picture}(1, ' + "{:.5f}".format(ratio) + ")%\n"
    pdftex += r'    \put(0,0){\includegraphics[width=\unitlength,page=1]{' + imagename + "}}%\n"

    for text in texts:
        x = float(text['x'])
        y = float(text['y'])
        s = text['text']
        pdftex += r'    \put' + \
            "({:.5f}, {:.5f})".format(x / width, (1 - y / height) * ratio)
        pdftex += r'{\color[rgb]{0,0,0}\makebox(0,0)[lb]{\smash{' + s + '}}}%' + "\n"

    pdftex += r'''  \end{picture}%
\endgroup%'''
    return pdftex


def tex_preview(imagename, preamble_text):
    tex = ""
    tex += r'''\documentclass{article}
\usepackage{amsmath}
\usepackage{amsthm}
\usepackage{amssymb}
\usepackage{amsfonts}
'''
    tex += r'''\usepackage{graphicx}
\usepackage{import}
\usepackage{xifthen}
\usepackage{pdfpages}
\usepackage{transparent}
'''
    if preamble_text:
        tex += "% USER PREAMBLE\n"
        tex += preamble_text
        tex += "\n"
    tex += r'\begin{document}' + "\n"
    tex += r'''\begin{figure}[ht]
  \def\svgwidth{0.6\columnwidth}
  \import{./}{''' + imagename + "}\n"
    tex += r'''\end{figure}
\end{document}
'''
    return tex


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Convert svg to pdf+pdf_tex template. Uses inkscape or cairosvg.',
        epilog="Given a file PIC.svg, this script overwrites files PIC.pdf and PIC.pdf_tex."
        " The option -g also overwrites a PIC-preview.tex"
        " file and compiles it (silently) using pdflatex."
               " The default conversion"
               " method is Inkscape. If the option -c is given or if Inkscape binary file"
               " cannot be found, the script uses a naive conversion using cairosvg. Note"
               " that the naive conversion DOES NOT support any kind of svg transformations"
               " (so it relies on something like a 'Flatten transforms' export option in"
               " the vector editing software)")
    parser.add_argument('-c', '--cairosvg', action='store_true', default=False,
                        help='use cairosvg conversion even if Inkscape is available')
    parser.add_argument('-g', '--generate-preview', action='store_true', default=False,
                        help='generate and compile a basic TeX document with the converted picture')
    parser.add_argument('-p', '--preamble', default=None,
                        help='add the contents of PREAMBLE to the preview document')
    parser.add_argument('-o', '--output-dir', default=None,
                        help='output directory')
    parser.add_argument('svgfile', default=None, help='source SVG file')
    options = parser.parse_args()

    inputfile = Path(options.svgfile).resolve()

    if options.output_dir:
        output_dir = Path(options.output_dir)
        _file = inputfile.stem
        pdf_file = output_dir / f'{_file}.pdf'
        pdftex_file = output_dir / f'{_file}.pdf_tex'
    else:
        pdf_file = inputfile.with_suffix('.pdf')
        pdftex_file = inputfile.with_suffix('.pdf_tex')

    inkscape = Path(INKSCAPE).resolve()

    if options.cairosvg or not inkscape.exists():
        # Make sure that cairosvg is available
        if not shutil.which('cairosvg'):
            sys.stderr.write("ERROR: cairosvg not found in $PATH\n")
            sys.exit(1)

        notext_image = inputfile.with_name(inputfile.stem + '-notext.svg')

        tree = ET.parse(inputfile)
        root = tree.getroot()
        width, height = extract_size(root)
        texts = extract_texts(root)

        # Produce an SVG image with all text elements omitted.
        remove_text(root)
        tree.write(notext_image)

        # Convert the produced SVG into a PDF image with cairosvg
        result = subprocess.run(
            ['cairosvg',  "-o",  str(pdf_file), str(notext_image)])
        if result.returncode is not 0:
            sys.stderr.write("ERROR: cairosvg didn't convert svg to pdf.\n")
            sys.exit(1)
        # Remove the temporary svg picture without text
        notext_image.unlink()

        # Write a .pdf_tex file
        pdftex = generate_pdftex(str(pdf_file), width, height, texts)
        with open(pdftex_file, 'w') as f:
            f.write(pdftex)

    else:  # we can use Inkscape
        result = subprocess.run([str(inkscape), "-D",
                                 str(inputfile),
                                 f"--export-filename={str(pdf_file)}",
                                 "--export-latex"])
        if result.returncode is not 0:
            sys.stderr.write("ERROR: inkscape didn't convert svg to pdf\n")
            sys.exit(1)

    # At this point the conversion has been done by either of the two methods,
    # so the preview file can be generated and compiled.
    if options.generate_preview:
        preamble_text = open(options.preamble, 'r').read(
        ) if options.preamble else None
        tex = tex_preview(pdf_file.name + '_tex', preamble_text)

        preview_file = inputfile.with_name(inputfile.stem + '-preview.tex')
        with open(preview_file, 'w') as f:
            f.write(tex)

        result = subprocess.run(['pdflatex', '-halt-on-error', str(preview_file)],
                                stdout=subprocess.DEVNULL)
        if result.returncode is not 0:
            sys.stderr.write("ERROR: pdflatex compilation error\n")
            sys.exit(1)
        # If the compilation is successful, clean up after pdflatex
        aux_file = preview_file.with_suffix('.aux')
        log_file = preview_file.with_suffix('.log')
        aux_file.unlink()
        log_file.unlink()

    sys.exit(0)
