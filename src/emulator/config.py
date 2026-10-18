"""Разбор параметров командной строки эмулятора."""

import argparse


def parse_args(argv=None):
    """Разобрать параметры запуска и вернуть объект с настройками."""
    parser = argparse.ArgumentParser(
        prog="emulator",
        description="Эмулятор командной оболочки UNIX-подобной ОС.",
    )
    parser.add_argument(
        "--vfs",
        metavar="PATH",
        help="путь к физическому расположению VFS",
    )
    parser.add_argument(
        "--script",
        metavar="PATH",
        help="путь к стартовому скрипту",
    )
    return parser.parse_args(argv)


def debug_lines(options):
    """Вернуть строки отладочного вывода всех заданных параметров."""
    return [
        f"[debug] vfs = {options.vfs}",
        f"[debug] script = {options.script}",
    ]
