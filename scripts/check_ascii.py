import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description="Checks all .tex files in a given directory (or file) "
                                             "for potentially harmful symbols (non ASCII).")

parser.add_argument("root",
                    help="Path to a directory containing .tex files or .tex file.")
parser.add_argument("--show-umlaute",
                    action="store_true",
                    help="Whether the output should show Umlaute (including ß).")

UMLAUTE = ("ä", "ü", "ö", "ß")

if __name__ == "__main__":
    args = parser.parse_args()

    root = Path(args.root)

    if root.is_dir():
        tex_files = list(root.glob("**/*.tex"))
    else:
        tex_files = [root]

    for file_path in tex_files:
        with open(file_path, "r", encoding="utf8") as f:
            lines = f.read().splitlines()
            for n_line, line in enumerate(lines, 1):
                for n_char, char in enumerate(line, 1):
                    if (ord(char) & ~127) != 0:
                        if (not args.show_umlaute) and (char.lower() in UMLAUTE):
                            continue

                        print("File {}:{}, char {} ({})".format(
                            file_path, n_line, n_char, char))
                        print(r"{}".format(line))
                        print("{:>{before}}".format("^", before=n_char))
