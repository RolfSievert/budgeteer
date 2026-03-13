# Budgeteer

A little helper to keep your budget :)

Features:
- Fullscreen command-line interface
- Tab-completion of expense names
- Automatic category assignment
- Yearly breakdown
- Monthly breakdown
- Automatic CSV export

TODO:
- custom start/end of month
- editable categories
- categorize uncategorize expenses

## Installation

### Arch linux

Two options:
1. Run `just install-arch` to install using pacman. (requires [just](https://github.com/casey/just))
2. Run the following code
```bash
python3 -m build
makepkg --syncdeps --force --clean
sudo pacman -U budgeteer-*-x86_64.pkg.tar.zst
```

### Using pip

I recommend installing with [pipx](https://github.com/pypa/pipx), and it is used just like pip is used.
```bash
python3 -m build
pipx install .
```

but if you want to, you can exchange `pipx` with `pip`.

## Requirements

Python packages
- `prompt_toolkit`
- `platformdirs`
- `sqlite3`

## Usage

Install the package and run `budgeteer --help` to see available commands.
