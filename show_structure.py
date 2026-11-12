
from pathlib import Path

ROOT = Path(__file__).resolve().parent

EXCLUDED = {
    ".venv",
    "venv",
    "__pycache__",
    ".git",
    ".idea",
    ".pytest_cache"
}


def print_tree(path: Path, prefix=""):
    items = sorted(
        [item for item in path.iterdir() if item.name not in EXCLUDED],
        key=lambda x: (x.is_file(), x.name.lower())
    )

    for index, item in enumerate(items):
        is_last = index == len(items) - 1
        connector = "└── " if is_last else "├── "

        print(prefix + connector + item.name)

        if item.is_dir():
            extension = "    " if is_last else "│   "
            print_tree(item, prefix + extension)


print(ROOT.name)
print_tree(ROOT)
