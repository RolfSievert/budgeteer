app_name := 'budgeteer'

@default:
    just --list

build:
    @python3 -m build

# run on a local test database
run *args:
    @# use -m so that imports are relative the package root
    python3 -m {{ app_name }}.main {{ args }} \
        --user-settings-path test/user-settings.json \
        --db-path test/test.sqlite \
        --backup-dir test

# install with pipx
[group('install')]
install: build
    @pipx install .

# install on arch linux
[group('install')]
install-arch:
    @makepkg --syncdeps --force --clean
    @sudo pacman -U {{ app_name }}*-x86_64.pkg.tar.zst

# uninstall with pip
[group('install')]
uninstall:
    @pip install pip-autoremove
    @pip-autoremove {{ app_name }} -y
