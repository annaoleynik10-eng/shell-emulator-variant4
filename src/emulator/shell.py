"""Ядро эмулятора: приглашение, цикл REPL и выполнение команд."""

import getpass
import socket

from emulator import commands
from emulator.errors import ShellError, ShellExit
from emulator.parser import parse_line
from emulator.vfs import ROOT_SYMBOL, SEPARATOR, VFS

MOTD_NAME = "motd"


class Shell:
    """Эмулятор командной оболочки UNIX-подобной ОС."""

    def __init__(self, output=print, vfs=None):
        """Подготовить оболочку, взяв имя пользователя и хоста из ОС."""
        self.user = getpass.getuser()
        self.host = socket.gethostname().split(".")[0]
        self.output = output
        self.vfs = vfs if vfs is not None else VFS(self.user)
        self.cwd = []

    def cwd_display(self):
        """Вернуть текущий каталог в виде для приглашения (~ - корень)."""
        return SEPARATOR.join([ROOT_SYMBOL] + self.cwd)

    def show_motd(self):
        """Вывести сообщение дня из файла motd в корне VFS, если он есть."""
        node = self.vfs.root.children.get(MOTD_NAME)
        if node is not None and not node.is_dir:
            self.output(node.text().rstrip("\n"))

    def prompt(self):
        """Сформировать приглашение вида user@host:~$."""
        return f"{self.user}@{self.host}:{self.cwd_display()}$ "

    def execute(self, line):
        """Выполнить одну строку ввода.

        Возвращает True при успехе и False при ошибке.
        Исключение ShellExit пробрасывается наружу.
        """
        try:
            parsed = parse_line(line)
        except ShellError as error:
            self.output(f"shell: {error}")
            return False
        if parsed is None:
            return True
        name, args = parsed
        handler = commands.COMMANDS.get(name)
        if handler is None:
            self.output(f"{name}: command not found")
            return False
        try:
            result = handler(self, args)
        except ShellError as error:
            self.output(f"{name}: {error}")
            return False
        if result:
            self.output(result)
        return True

    def run_script(self, path):
        """Выполнить стартовый скрипт построчно.

        Каждая команда выводится вместе с приглашением, как будто её
        ввёл пользователь. Пустые строки и комментарии (#) пропускаются,
        строки с ошибками тоже пропускаются - выполнение продолжается.
        Возвращает число строк, завершившихся ошибкой.
        """
        try:
            with open(path, encoding="utf-8") as file:
                lines = file.read().splitlines()
        except OSError as error:
            raise ShellError(f"cannot read script: {path}") from error
        failed = 0
        for line in lines:
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            self.output(self.prompt() + line)
            if not self.execute(line):
                failed += 1
        return failed

    def run_interactive(self, read=input):
        """Запустить диалог с пользователем и вернуть код завершения."""
        while True:
            try:
                line = read(self.prompt())
            except EOFError:
                self.output("")
                return 0
            except KeyboardInterrupt:
                self.output("^C")
                continue
            try:
                self.execute(line)
            except ShellExit as stop:
                return stop.code
