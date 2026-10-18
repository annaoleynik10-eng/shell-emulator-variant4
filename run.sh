#!/bin/sh
# Запуск эмулятора командной оболочки.
# Все аргументы передаются эмулятору без изменений.
DIR=$(cd "$(dirname "$0")" && pwd)
PYTHONPATH="$DIR/src" exec python3 -m emulator "$@"
