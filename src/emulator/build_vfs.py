"""Сборка ZIP-образа VFS из обычной папки.

Архивы не хранятся в репозитории, поэтому тестовые VFS лежат в виде
папок в tests/vfs и собираются в ZIP перед запуском эмулятора:

    python3 -m emulator.build_vfs ПАПКА АРХИВ.zip
"""

import os
import sys
import zipfile

USAGE = "usage: python3 -m emulator.build_vfs SOURCE_DIR OUTPUT_ZIP"
ARGS_COUNT = 2


def build(source_dir, output_zip):
    """Упаковать содержимое папки в ZIP (пути относительно папки)."""
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        for root, dirs, files in os.walk(source_dir):
            dirs.sort()
            for name in dirs + sorted(files):
                full = os.path.join(root, name)
                archive.write(full, os.path.relpath(full, source_dir))


def main(argv):
    """Разобрать аргументы и собрать архив. Вернуть код завершения."""
    if len(argv) != ARGS_COUNT or not os.path.isdir(argv[0]):
        print(USAGE, file=sys.stderr)
        return 1
    build(argv[0], argv[1])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
