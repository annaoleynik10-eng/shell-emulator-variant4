"""Ядро эмулятора: приглашение, цикл REPL и выполнение команд."""

import getpass
import socket

from emulator import commands
from emulator.errors import ShellError, ShellExit
from emulator.parser import parse_line


class Shell:
    """Эмулятор командной оболочки UNIX-подобной ОС."""

    def __init__(self, output=print):
        """Подготовить оболочку, взяв имя пользователя и хоста из ОС."""
        self.user = getpass.getuser()
        self.host = socket.gethostname().split(".")[0]
        self.output = output

    def cwd_display(self):
        """Вернуть текущий каталог в виде для приглашения."""
        return "~"

    def prompt(self):
        """Сформировать приглашение вида user@host:~$."""
        return f"{self.user}@{self.host}:{self.cwd_display()}$ "

    def execute(self, line):
        """Выполнить одну строку ввода.

        Возвращает True при успехе и False при ошибке.
        Исключение ShellExit пробрасывается наружу.
        """
        parsed = parse_line(line)
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
