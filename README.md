# Budgeteer

[short summary of what this is]

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

- `prompt_toolkit` python package

## Usage

Install the package and run `budgeteer --help` to see available commands.

### Examples

