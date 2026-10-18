#!/bin/sh
# Этап 4: проверка ls, cd, uniq, find, rev на глубокой VFS.
# Запуск из корня репозитория: ./tests/sh/stage4.sh
cd "$(dirname "$0")/../.." || exit 1
. tests/sh/build_vfs.sh
./run.sh --vfs "$VFS_DIR/deep.zip" --script tests/startup/stage4.txt
rm -rf "$VFS_DIR"
