import json
import os
import subprocess
from pathlib import Path
from pprint import pprint

import filehash

if __name__ == "__main__":
    this_file = Path(__file__)
    os.chdir(this_file.parents[1])
    cache_file = this_file.parent/"cache.json"

    if cache_file.exists():
        with open(cache_file, 'r') as f:
            cache = json.load(f)
    else:
        cache = dict()

    root = Path(os.getcwd())

    svgs = [str(x) for x in root.glob("**/svg_source/*.svg")]

    changed = list()

    sha512hasher = filehash.FileHash()

    for file in svgs:
        _hash = sha512hasher.hash_file(file)
        if file in cache.keys():
            if cache[file] != _hash:
                cache[file] = _hash
                changed.append(file)

        else:
            cache[file] = _hash
            changed.append(file)

    for change in changed:
        _path = Path(change).parents[1]
        command = ['python', 'scripts/svg2pdftex.py', f'{change}', '-o', f'{_path}']
        print(f"Running {' '.join(command)}...")
        proc = subprocess.run(command)
        if proc.returncode != 0:
            print(f"{change} failed!")
            exit(1)

    print(f"Changes:")
    pprint(changed)

    with open(cache_file, "w") as f:
        json.dump(cache, f, indent=4, sort_keys=True)

    exit(0)




