"""Реализация команд эмулятора.

Каждая команда - функция вида cmd_имя(shell, args), которая
возвращает текст для вывода или вызывает ShellError.
"""

import fnmatch
import itertools

from emulator.errors import ShellError, ShellExit
from emulator.vfs import CURRENT_DIR, SEPARATOR

MAX_EXIT_ARGS = 1
MAX_CD_ARGS = 1
SINGLE_PATH = 1
SINGLE_OCCURRENCE = 1
OPTION_WITH_VALUE = 2
FIND_OPTIONS = ("-name", "-type")
FIND_TYPES = {"f": False, "d": True}
DIR_MODE = "drwxr-xr-x"
FILE_MODE = "-rw-r--r--"
COUNT_WIDTH = 7


def lookup(shell, path):
    """Найти узел VFS по пути. Вернуть (список имён, узел)."""
    parts = shell.vfs.resolve(shell.cwd, path)
    node = shell.vfs.get(parts)
    if node is None:
        raise ShellError(f"{path}: No such file or directory")
    return parts, node


def read_lines(shell, path):
    """Прочитать файл VFS и вернуть список его строк."""
    _, node = lookup(shell, path)
    if node.is_dir:
        raise ShellError(f"{path}: Is a directory")
    return node.text().splitlines()


def split_flags(args, allowed):
    """Отделить флаги (-x) от остальных аргументов.

    Флаги вида -lR раскладываются на отдельные -l и -R.
    Неизвестный флаг вызывает ShellError.
    """
    flags, rest = set(), []
    for arg in args:
        if not arg.startswith("-") or arg == "-":
            rest.append(arg)
            continue
        for letter in arg[1:]:
            if f"-{letter}" not in allowed:
                raise ShellError(f"invalid option -- '{letter}'")
            flags.add(f"-{letter}")
    return flags, rest


def format_entry(node, long_format):
    """Отформатировать одну запись для вывода ls."""
    if not long_format:
        return node.name
    mode = DIR_MODE if node.is_dir else FILE_MODE
    return f"{mode} {node.owner:<8} {node.size():>6} {node.name}"


def list_node(node, long_format):
    """Вернуть строки вывода ls для файла или содержимого каталога."""
    if not node.is_dir:
        return [format_entry(node, long_format)]
    children = sorted(node.children.values(), key=lambda item: item.name)
    entries = [format_entry(child, long_format) for child in children]
    if long_format:
        return entries
    return ["  ".join(entries)] if entries else []


def cmd_ls(shell, args):
    """Показать содержимое каталога: ls [-l] [путь ...]."""
    flags, paths = split_flags(args, {"-l"})
    paths = paths or [CURRENT_DIR]
    blocks = []
    for path in paths:
        _, node = lookup(shell, path)
        lines = list_node(node, "-l" in flags)
        if len(paths) > SINGLE_PATH:
            lines.insert(0, f"{path}:")
        blocks.append("\n".join(lines))
    return "\n\n".join(block for block in blocks if block)


def cmd_cd(shell, args):
    """Сменить текущий каталог: cd [путь]. Без аргумента - в корень."""
    if len(args) > MAX_CD_ARGS:
        raise ShellError("too many arguments")
    if not args:
        shell.cwd = []
        return ""
    parts, node = lookup(shell, args[0])
    if not node.is_dir:
        raise ShellError(f"{args[0]}: Not a directory")
    shell.cwd = parts
    return ""


def cmd_uniq(shell, args):
    """Убрать подряд идущие повторы строк: uniq [-c] [-d] файл."""
    flags, paths = split_flags(args, {"-c", "-d"})
    if len(paths) != SINGLE_PATH:
        raise ShellError("expected exactly one file")
    result = []
    for line, group in itertools.groupby(read_lines(shell, paths[0])):
        count = len(list(group))
        if "-d" in flags and count == SINGLE_OCCURRENCE:
            continue
        if "-c" in flags:
            line = f"{count:>{COUNT_WIDTH}} {line}"
        result.append(line)
    return "\n".join(result)


def cmd_rev(shell, args):
    """Перевернуть каждую строку файлов: rev файл [файл ...]."""
    if not args:
        raise ShellError("missing file operand")
    result = []
    for path in args:
        result.extend(line[::-1] for line in read_lines(shell, path))
    return "\n".join(result)


def parse_find_args(args):
    """Разобрать аргументы find: [путь] [-name шаблон] [-type f|d]."""
    start = CURRENT_DIR
    if args and not args[0].startswith("-"):
        start, args = args[0], args[1:]
    options = {}
    while args:
        if args[0] not in FIND_OPTIONS:
            raise ShellError(f"unknown predicate '{args[0]}'")
        if len(args) < OPTION_WITH_VALUE:
            raise ShellError(f"missing argument to '{args[0]}'")
        options[args[0]] = args[1]
        args = args[OPTION_WITH_VALUE:]
    if options.get("-type", "f") not in FIND_TYPES:
        raise ShellError(f"unknown argument to -type: {options['-type']}")
    return start, options


def walk(node, display):
    """Обойти дерево в глубину, выдавая пары (путь для вывода, узел)."""
    yield display, node
    for name in sorted(node.children):
        child_path = display.rstrip(SEPARATOR) + SEPARATOR + name
        yield from walk(node.children[name], child_path)


def find_matches(node, display, options):
    """Проверить, подходит ли узел под условия -name и -type."""
    name = node.name or display
    if "-name" in options and not fnmatch.fnmatch(name, options["-name"]):
        return False
    if "-type" in options:
        return node.is_dir == FIND_TYPES[options["-type"]]
    return True


def cmd_find(shell, args):
    """Найти файлы: find [путь] [-name шаблон] [-type f|d]."""
    start, options = parse_find_args(args)
    _, node = lookup(shell, start)
    return "\n".join(
        display for display, item in walk(node, start)
        if find_matches(item, display, options))


def cmd_exit(shell, args):
    """Завершить работу эмулятора: exit [код]."""
    del shell
    if len(args) > MAX_EXIT_ARGS:
        raise ShellError("too many arguments")
    if not args:
        raise ShellExit(0)
    try:
        code = int(args[0])
    except ValueError as error:
        raise ShellError(f"{args[0]}: numeric argument required") from error
    raise ShellExit(code)


def cmd_vfs_info(shell, args):
    """Служебная команда: показать источник и размер VFS."""
    if args:
        raise ShellError("too many arguments")
    dirs, files = shell.vfs.count()
    source = shell.vfs.source or "(empty VFS)"
    return f"source: {source}\ndirectories: {dirs}\nfiles: {files}"


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "uniq": cmd_uniq,
    "find": cmd_find,
    "rev": cmd_rev,
    "exit": cmd_exit,
    "vfs-info": cmd_vfs_info,
}
