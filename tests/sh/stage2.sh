#!/bin/sh
# Этап 2: проверка всех параметров командной строки.
# Запуск из корня репозитория: ./tests/sh/stage2.sh
cd "$(dirname "$0")/../.." || exit 1
. tests/sh/build_vfs.sh

echo "=== 1. Без параметров (ввод пуст - сразу выход)"
./run.sh < /dev/null

echo "=== 2. Только путь к VFS"
./run.sh --vfs "$VFS_DIR/minimal.zip" < /dev/null

echo "=== 3. Только стартовый скрипт"
./run.sh --script tests/startup/stage2.txt

echo "=== 4. Оба параметра"
./run.sh --vfs "$VFS_DIR/deep.zip" --script tests/startup/stage2.txt

echo "=== 5. Скрипт без exit, затем диалог"
echo "ls" | ./run.sh --vfs "$VFS_DIR/deep.zip" \
    --script tests/startup/stage2_no_exit.txt

echo "=== 6. Ошибка: скрипт не существует"
./run.sh --script no_such_script.txt
echo "код завершения: $?"

echo "=== 7. Ошибка: VFS не существует"
./run.sh --vfs no_such_vfs.zip
echo "код завершения: $?"

echo "=== 8. Ошибка: неизвестный параметр"
./run.sh --unknown 2>&1
echo "код завершения: $?"

rm -rf "$VFS_DIR"
