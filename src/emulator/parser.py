"""Парсер строки ввода."""

import shlex

from emulator.errors import ShellError


def parse_line(line):
    """Разделить строку на команду и аргументы по пробелам.

    Как и в настоящей оболочке, кавычки группируют слова с пробелами
    и не попадают в аргументы: echo "a b" даёт один аргумент a b.
    Возвращает кортеж (команда, список аргументов) или None,
    если строка пустая или состоит только из пробелов.
    """
    try:
        parts = shlex.split(line)
    except ValueError as error:
        raise ShellError(f"syntax error: {error}") from error
    if not parts:
        return None
    return parts[0], parts[1:]
