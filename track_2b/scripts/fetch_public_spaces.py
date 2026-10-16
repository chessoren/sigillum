"""Research step (needs internet, run once): shallow-clone every public Hugging
Face Space whose name or card mentions Apertus, without LFS files.

    python3 scripts/fetch_public_spaces.py /tmp/apertus-spaces
    PYTHONPATH=src python3 -m sigillum community /tmp/apertus-spaces

Only the aggregate is kept (data/community/aggregate.json). The clones are
deleted afterwards and no project is named.
"""

import json
import os
import subprocess
import sys
import urllib.request

dest = sys.argv[1] if len(sys.argv) > 1 else "/tmp/apertus-spaces"
os.makedirs(dest, exist_ok=True)
api = "https://huggingface.co/api/spaces?search=apertus&limit=500"
spaces = json.load(urllib.request.urlopen(api, timeout=30))
for i, s in enumerate(spaces):
    target = os.path.join(dest, f"p{i:03d}")  # anonymous folder names
    if not os.path.exists(target):
        subprocess.run(["git", "clone", "--depth", "1", "--quiet", f"https://huggingface.co/spaces/{s['id']}", target],
                       env={**os.environ, "GIT_LFS_SKIP_SMUDGE": "1", "GIT_TERMINAL_PROMPT": "0"}, check=False)
print(f"{len(spaces)} public Spaces cloned into {dest}")
