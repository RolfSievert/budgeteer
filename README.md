# Budgeteer

A little helper to keep your budget :)


## ✨ Features
- 🖥️ **Full-screen** command-line interface
- ⌨️ **Tab completion** for expense names & categories
- 🏷️ **Auto categorize** repeated expenses
- 📊 **Yearly** and **monthly** breakdowns
- 📤 **CSV export**
- 💾 **Backed by SQLite**


## 📦 Installation

### Arch Linux (via `pacman`)

**Option 1: (requires [just](https://github.com/casey/just))**
```bash
just install-arch
```

**Option 2: Manual**
```bash
python3 -m build
makepkg --syncdeps --force --clean
sudo pacman -U budgeteer-*.pkg.tar.zst
```

### Universal (pip/pipx)

I recommend installing with [pipx](https://github.com/pypa/pipx), and it is used just like pip.
```bash
python3 -m build
pipx install .
```

but if you want to, you can exchange `pipx` with `pip`.


## Requirements

- `prompt_toolkit`
- `platformdirs`


## Usage

```bash
budgeteer --help
```

Run **`budgeteer`** after installation to start using it.


## 🚧 TODO
- Monthly reminders
- Custom start-of-month day
- CSV import
- Editable categories
- Uncategorized expenses view
