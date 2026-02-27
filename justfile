app_name := 'budgeteer'

@default:
    just --list

build:
    @python3 -m build

run:
    @./budgeteer/main.py

install: build
    @pipx install .

install-arch:
    @makepkg --syncdeps --force --clean
    @sudo pacman -U {{app_name}}*-x86_64.pkg.tar.zst

uninstall:
    @pip install pip-autoremove
    @pip-autoremove {{app_name}} -y
