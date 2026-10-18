#!/bin/sh
# Собрать ZIP-образы тестовых VFS во временную папку.
# Использование: . tests/sh/build_vfs.sh  (задаёт переменную VFS_DIR)
VFS_DIR=$(mktemp -d)
for name in minimal several deep; do
    PYTHONPATH=src python3 -m emulator.build_vfs \
        "tests/vfs/$name" "$VFS_DIR/$name.zip"
done
# Двоичный файл для проверки base64 создаётся на лету:
# двоичные файлы не хранятся в репозитории.
mkdir -p "$VFS_DIR/bin_src/bin"
cp -R tests/vfs/deep/. "$VFS_DIR/bin_src/"
printf '\000\001\002\377\376' > "$VFS_DIR/bin_src/bin/data.bin"
PYTHONPATH=src python3 -m emulator.build_vfs \
    "$VFS_DIR/bin_src" "$VFS_DIR/deep.zip"
printf 'not a zip' > "$VFS_DIR/broken.zip"
