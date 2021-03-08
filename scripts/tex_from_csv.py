import argparse
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(
    description="Create LaTeX document from csv file containing Chapters and Sections.")

parser.add_argument("infile",
                    help="CSV input file.")

parser.add_argument("name",
                    help="Name of the startet document")

if __name__ == "__main__":
    args = parser.parse_args()

    infile = Path(args.infile)
    name = args.name

    chapters = []
    sections = []

    data = []
    with open(infile, "r") as f:
        data = f.readlines()

    for d in data:
        d = [_d.strip() for _d in d.split(",")]
        if len(d) > 0 and d[0] != '':
            chapters.append(d[0])
            sections.append([_d for _d in d[1:] if _d != ''])
    
    for chp, secs in zip(chapters, sections):
        command = ['python', 'scripts/tex_manager.py', '-i', '-a', args.name, chp]
        for sec in secs:
            command += ['-s', sec]
        print(f"Running {' '.join(command)}")
        subprocess.run(command)
    
    print("Done.")
