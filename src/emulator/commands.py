"""Реализация команд эмулятора.

Каждая команда - функция вида cmd_имя(shell, args), которая
возвращает текст для вывода или вызывает ShellError.
"""

from emulator.errors import ShellError, ShellExit

MAX_EXIT_ARGS = 1


def cmd_ls(shell, args):
    """Заглушка ls: вывести имя команды и аргументы."""
    del shell
    return f"ls: args={args}"


def cmd_cd(shell, args):
    """Заглушка cd: вывести имя команды и аргументы."""
    del shell
    return f"cd: args={args}"


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
    "exit": cmd_exit,
    "vfs-info": cmd_vfs_info,
}
