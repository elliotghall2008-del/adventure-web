"""Copy the generated browser game into the GitHub Pages folder."""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parent
source = root / "game" / "build" / "web"
destination = root / "docs"

if not (source / "index.html").is_file():
    raise SystemExit("Build first: python -m pygbag --build game")

# docs is generated output: do not store hand-written files there.
if destination.exists():
    shutil.rmtree(destination)
shutil.copytree(source, destination)
(destination / ".nojekyll").touch()
print("Ready: docs/index.html")