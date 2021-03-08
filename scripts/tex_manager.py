import argparse
import os
import shutil
import sys
from pathlib import Path

import jinja2

parser = argparse.ArgumentParser(
    description="Helper for LaTeX Chapter and Section generation.")

parser.add_argument("document",
                    help="The documents root path.")

parser.add_argument("chapter",
                    help="Chapter name. Will be startet automatically if not already existing.")

parser.add_argument("-s", "--sections",
                    help="Section(s) to start.",
                    action="append")

parser.add_argument("-i", "--insert",
                    help="Try inserting input/include statements in according files.",
                    action="store_true")

parser.add_argument("-a", "--append",
                    help="Alle insert attempts are appended.",
                    action="store_true")


def write_template(path, content):
    with open(path, "w") as f:
        f.write(content)


def start_document(name, template):
    shutil.copytree(template, name)
    os.rename(Path(name)/"Document.tex", Path(name)/f"{name}.tex")


def index_prompt(options):
    """Trys to get a choice from the user.
    Returns -1 if failed.

    Args:
        options (list): list of options

    Returns:
        int: index of choice or None if failed
    """
    for i, opt in enumerate(options, 1):
        print("  {:0>2}: {}".format(i, opt))

    if len(options) == 0:
        return 0

    print("Leave empty to append.")
    choice = input(f"Choose 1-{len(options)}: ")
    if choice == "":
        return len(options)
    try:
        return int(choice) - 1
    except ValueError:
        return None


def insert_includes(parse_file, to_include, start, end, function='include', append=False):
    with open(parse_file, "r+") as f:
        lines = f.readlines()
        stripped = [l.strip() for l in lines]
        try:
            section_start = stripped.index(start)
            section_end = stripped.index(end)

            includes = stripped[section_start+1:section_end]
            includes = [incl for incl in includes if not (
                incl == "" or incl.startswith("%"))]

            options = [opt.split("{")[1].split("}")[0] for opt in includes]
            if to_include in options:
                print(f"{to_include} already included")
            else:
                print(f"Inserting {to_include}")
                if append:
                    idx = len(options)
                else:
                    idx = index_prompt(options)
                if idx is None:
                    print(f"Invalid input, skipping {to_include}")
                else:
                    includes.insert(idx, f"\\{function}{{{to_include}}}")
                    includes = [incl + "\n" for incl in includes]

                    output = lines[:section_start+1] + \
                        includes + lines[section_end:]
                    f.seek(0)
                    f.writelines(output)
                    f.truncate()

        except ValueError:
            print(f"Could not match {start} {end} section in {parse_file}.")


if __name__ == "__main__":
    script_root = Path(Path(sys.argv[0]).parent)

    # setupt jinja environment
    template_loader = jinja2.FileSystemLoader(script_root/"templates")
    template_env = jinja2.Environment(loader=template_loader)

    args = parser.parse_args()

    root = Path(args.document)

    if not (root.exists() and root.is_dir()):
        print("Document does not exist, creating it...")
        start_document(args.document, script_root/"templates/Document")

    main_file = list(root.glob("*.tex"))
    if len(main_file) == 1:
        main_file = main_file[0]
    else:
        print(f"No or too many main files were located: {main_file}")

    chapter_name = args.chapter.strip()
    chapter_underscore = chapter_name.replace(" ", "_")
    chapter_label = chapter_name.replace(" ", "")
    chapter_path = Path(chapter_underscore)

    chapter_path = root / chapter_path

    if chapter_path.is_dir():
        print(f"Found {chapter_path}.")
    else:
        print(f"Creating {chapter_path}...")
        # create Chapter directory
        chapter_path.mkdir(exist_ok=True)

    # create figures dir
    (chapter_path / "figures/svg_source").mkdir(exist_ok=True, parents=True)

    section_names = [] if args.sections is None else args.sections
    section_underscore = [s.replace(" ", "_") for s in section_names]
    section_labels = [s.replace(" ", "") for s in section_names]

    # ─── FORMAT TEX FILE ────────────────────────────────────────────────────────────

    format_file = chapter_path / "Format.tex"
    if not format_file.exists():
        print("Creating Format.tex file...")
        format_template = template_env.get_template("format.tex.jinja2")

        content = format_template.render(chapter=chapter_name,
                                         chapter_tex_path=chapter_underscore,
                                         chapter_label=chapter_label,
                                         sections=section_underscore)
        write_template(format_file, content)

    # ─── CHAPTER TEX FILE ───────────────────────────────────────────────────────────

    chapter_file = chapter_path / f"{chapter_underscore}.tex"
    if not chapter_file.exists():
        print(f"Creating {chapter_underscore}.tex file...")
        chapter_template = template_env.get_template("chapter.tex.jinja2")

        content = chapter_template.render(chapter=chapter_name)
        write_template(chapter_file, content)
        if args.insert:
            insert_includes(main_file,
                            f"{chapter_underscore}/Format.tex",
                            start="%++ CHAPTERS ++%",
                            end="%-- CHAPTERS --%",
                            function="include",
                            append=args.append)

    # ─── SECTIONS TEX FILE ───────────────────────────────────────────────────────────

    sec_template = template_env.get_template("section.tex.jinja2")

    for i_sec in range(len(section_names)):
        sec_file = chapter_path / f"section_{section_underscore[i_sec]}.tex"
        if not sec_file.exists():
            print(f"Creating {section_underscore[i_sec]}.tex file...")

            content = sec_template.render(section_name=section_names[i_sec],
                                          section_label=section_labels[i_sec],
                                          chapter=chapter_label)
            write_template(sec_file, content)
            if args.insert:
                insert_includes(format_file,
                                f"\\thisChapter/section_{section_underscore[i_sec]}.tex",
                                start="%++ SECTIONS ++%",
                                end="%-- SECTIONS --%",
                                function="input",
                                append=args.append)
