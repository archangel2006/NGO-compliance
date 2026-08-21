from pathlib import Path

ignore = {
    "__pycache__",
    ".venv",
    "venv",
    "site-packages",
    "node_modules",
    ".git",
    "vectorstore"
}

def tree(path, prefix=""):
    items = sorted(Path(path).iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
    items = [i for i in items if i.name not in ignore]

    for i, item in enumerate(items):
        last = i == len(items)-1
        connector = "└── " if last else "├── "
        print(prefix + connector + item.name)
        if item.is_dir():
            tree(item, prefix + ("    " if last else "│   "))

tree("backend")