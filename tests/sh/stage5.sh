#!/bin/sh
# Этап 5: проверка chown и help. Второй запуск показывает,
# что изменения VFS не сохраняются: они делались только в памяти.
# Запуск из корня репозитория: ./tests/sh/stage5.sh
cd "$(dirname "$0")/../.." || exit 1
. tests/sh/build_vfs.sh
./run.sh --vfs "$VFS_DIR/deep.zip" --script tests/startup/stage5.txt
echo "=== Повторный запуск: владельцы снова исходные"
echo "ls -l etc" | ./run.sh --vfs "$VFS_DIR/deep.zip"
rm -rf "$VFS_DIR"
