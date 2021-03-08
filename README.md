# LaTeX-Template

**This project is its very early stages**

This is a latex document generator.
It aims towards reducing the labour of creating chapter, and sections.
With a few simple python scripts you are able to start a new document, insert chapters and section while not having to bother about any imports.

### Installation

Before getting started there are a few things to configure first.
First of all you will need to install python3.5+ and latex.
I will assume you are able to scavenge these tutorials from some where else. 

Lets clone the repo:
```bash
git clone https://github.com/TGCAras/LaTeX-Template.git
```

This will create a folder 'LaTeX-Template' in your current directory, lets enter it:
```bash
cd LaTeX-Template
```

I recommend setting up a virtual environment first and installing the 2 tiny dependencies this needs.
```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.text
```
On Windows probably something like this:  
```bash
py -m venv venv
& ./venv/Scripts/Activate.ps1
pip3 install -r requirements.text
```

This is basically it in terms of setting up!

### Getting started

Now lets discuss how we start a document.

#### From a csv file

If you already know most of your layout the easiest way is to just start by creating a csv file laying out all your chapters and sections.  
Basically each row in your csv file representative of a chapter, the first column being the chapters name and each following column being a section of this chapter.

Lets do an example:
| Chapter             | Section 1      | Section 2       | Section 3      |
|---------------------|----------------|-----------------|----------------|
| Introduction        | Basics         | Notation        |                |
| State of the Art    | My First Topic | My Second Topic | My Third Topic |
| Contributes         | I did this     |                 |                |
| Summary and Outlook | Summary        | Outlook         |                |

We now have 4 chapters with different amounts of sections defined.
Pleas note that the csv file should not contain any header!
The plain file should look like this:  
`document.csv`:
```
Introduction,Basics,Notation,
State of the Art,My First Topic,My Second Topic,My Third Topic
Contributes,I did this,,,
Summary and Outlook,Summary,Outlook,
```

To generate this document lets run the following from the root of this repo, assuming we created the csv file within the root of the repo:
```bash
python scripts/tex_from_csv.py document.csv Thesis
```
Thesis denotes the name name of the Document, in other word the name of the main .tex file and the directories name.

We'll end up with this structure:
```bash
LaTeX-Template\Thesis
│   Literature.bib
│   Thesis.tex
│
├───Appendix
│       Appendix.tex
│       Format.tex
│
├───Contributes
│   │   Contributes.tex
│   │   Format.tex
│   │   section_I_did_this.tex
│   │
│   └───figures
│       └───svg_source
├───Generic
│       Commands.tex
│       Format.tex
│       myData.tex
│       Notation.tex
│
├───Introduction
│   │   Format.tex
│   │   Introduction.tex
│   │   section_Basics.tex
│   │   section_Notation.tex
│   │
│   └───figures
│       └───svg_source
├───State_of_the_Art
│   │   Format.tex
│   │   section_My_First_Topic.tex
│   │   section_My_Second_Topic.tex
│   │   section_My_Third_Topic.tex
│   │   State_of_the_Art.tex
│   │
│   └───figures
│       └───svg_source
├───Summary_and_Outlook
│   │   Format.tex
│   │   section_Outlook.tex
│   │   section_Summary.tex
│   │   Summary_and_Outlook.tex
│   │
│   └───figures
│       └───svg_source
├───Table_of_Contents
│   │   Format.tex
│   │   Table_of_Contents.tex
│   │
│   └───figures
│           .gitkeep
│
└───Title_Page
    │   Format.tex
    │   Front_Page.tex
    │
    └───figures
            .gitkeep
```

Notice how the names have been converted to the chapter names and a bunch of default "Chapters" have been created.

Also all import in the ``Thesis.tex`` file and the ``Format.tex`` of each chapter are correct already.
You are now ready to go!

#### Adding Chapters and Segments separately via command line

We can also use the ``tex_manager.py`` script to add documents, chapters and section manually while **still not struggling with imports**.

This would create a chapter called Preface and prompt you at which place you wish to insert the new chapter among the others. In this case I entered '1' to add it at the very top.
```bash
>>> python scripts/tex_manager.py "Thesis" "Preface" -i
Creating Thesis\Preface...
Creating Format.tex file...
Creating Preface.tex file...
Inserting Preface/Format.tex
  01: Introduction/Format.tex
  02: State_of_the_Art/Format.tex
  03: Contributes/Format.tex
  04: Summary_and_Outlook/Format.tex
Leave empty to append.
Choose 1-4: 1
```

We can now see the Preface chapter in our folder structure:
```bash
├───Preface
│   │   Format.tex
│   │   Preface.tex
│   │
│   └───figures
│       └───svg_source
```
and the correct include statements in the ``Thesis.tex`` main file:
```latex
%++ CHAPTERS ++%
\include{Introduction/Format.tex}
\include{State_of_the_Art/Format.tex}
\include{Contributes/Format.tex}
\include{Summary_and_Outlook/Format.tex}
%-- CHAPTERS --%
```
This command will also create the document if not present.

The `-i` flag stands for insert and is responsible for inserting the include and input statements.
Not passing this flag will only create the files without managing your includes/inputs.

**A quick note: Do not remove the comments around the chapter includes and the section inputs as they are important for detecting the correct statements and not altering any of your own TeX text.**

We can also add a few sections to this chapter as follows:
```bash
>>> python scripts/tex_manager.py "Thesis" "Preface" -i -s "Stuff" -s "More Stuff" -s "Even More Stuff"
Found Thesis\Preface.
Creating Stuff.tex file...
Inserting \thisChapter/section_Stuff.tex
Creating More_Stuff.tex file...
Inserting \thisChapter/section_More_Stuff.tex
  01: \thisChapter/section_Stuff.tex
Leave empty to append.
Choose 1-1:
Creating Even_More_Stuff.tex file...
Inserting \thisChapter/section_Even_More_Stuff.tex
  01: \thisChapter/section_Stuff.tex
  02: \thisChapter/section_More_Stuff.tex
Leave empty to append.
Choose 1-2:
```

Hitting enter 2 times will just append the 3 new sections after each other, we can also set the `-a` append flag to automatically append all sections in the order we passed them.

The folder structure now looks like this:
```
├───Preface
│   │   Format.tex
│   │   Preface.tex
│   │   section_Even_More_Stuff.tex
│   │   section_More_Stuff.tex
│   │   section_Stuff.tex
│   │
│   └───figures
│       └───svg_source
```

And the inputs in `Preface/Format.tex`:
```latex
%++ SECTIONS ++%
\input{\thisChapter/section_Stuff.tex}
\input{\thisChapter/section_More_Stuff.tex}
\input{\thisChapter/section_Even_More_Stuff.tex}
%-- SECTIONS --%
```

### SVG to pdf_tex
You may have notices that the chapters also create a figures and svg_source folder.
This is because there is a python script in place converting each svg file in any svg_source folder to a .pdf_tex + .pdf file.

For this lets have a look at the ``Generic/Commands.tex`` file:
```latex
\newcommand*{\python}{../venv/Scripts/python.exe}
\newcommand*{\svgscriptlocation}{../scripts/detect_file_changes.py}

\immediate\write18{\python \svgscriptlocation}
```

Here you can replace both the python executable path as well as the path to the `detect_file_changes.py` script.

You will also have to replace the ``INKSCAPE = r"D:\\Tools\\Inkscape\\bin\\inkscape.exe"`` statement in the `svg2pdftex.py` script to what ever your inkscape installation path is.

On windows you can run the following after a successful installation to determine the path:
```powershell
get-command inkscape.exe
```

On linux and mac(?) you should be able to run
```bash
which inkscape
```

Also make sure to enable \wirte18 in your latex editor if you want all svgs to be converted while compiling your TeX document.
The `detect_file_changes.py` script is a wrapper for `svg2pdftex.py` and takes care of detecting files and tracking changes to avoid convert svgs without any changes happening.


