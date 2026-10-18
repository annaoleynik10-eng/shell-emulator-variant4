#!/bin/sh
# Этап 3: запуск эмулятора с разными вариантами VFS.
# Запуск из корня репозитория: ./tests/sh/stage3.sh
cd "$(dirname "$0")/../.." || exit 1
. tests/sh/build_vfs.sh

for name in minimal several deep; do
    echo "=== VFS: $name"
    ./run.sh --vfs "$VFS_DIR/$name.zip" --script tests/startup/stage3.txt
done

echo "=== Без VFS (пустая файловая система)"
./run.sh --script tests/startup/stage3.txt

echo "=== Ошибка: архив не существует"
./run.sh --vfs "$VFS_DIR/missing.zip"
echo "код завершения: $?"

echo "=== Ошибка: файл не является ZIP-архивом"
./run.sh --vfs "$VFS_DIR/broken.zip"
echo "код завершения: $?"

rm -rf "$VFS_DIR"
