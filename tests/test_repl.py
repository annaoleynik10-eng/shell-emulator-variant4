"""Тесты этапа 1: парсер, заглушки команд и exit."""

import unittest

from emulator.parser import parse_line
from emulator.shell import Shell


def make_shell():
    """Создать оболочку, которая копит вывод в список."""
    lines = []
    return Shell(output=lines.append), lines


class ParserTest(unittest.TestCase):
    """Проверки парсера строки."""

    def test_split_by_spaces(self):
        """Команда и аргументы разделяются пробелами."""
        self.assertEqual(parse_line("ls  -l   /home"), ("ls", ["-l", "/home"]))

    def test_empty_line(self):
        """Пустая строка даёт None."""
        self.assertIsNone(parse_line("   "))


class ReplTest(unittest.TestCase):
    """Проверки цикла REPL."""

    def test_prompt_format(self):
        """Приглашение содержит пользователя и хост."""
        shell, _ = make_shell()
        self.assertEqual(shell.prompt(), f"{shell.user}@{shell.host}:~$ ")

    def test_unknown_command(self):
        """Неизвестная команда сообщает об ошибке."""
        shell, lines = make_shell()
        self.assertFalse(shell.execute("foo bar"))
        self.assertEqual(lines, ["foo: command not found"])

    def test_exit_code(self):
        """exit с аргументом возвращает этот код."""
        shell, _ = make_shell()
        inputs = iter(["exit 3"])
        self.assertEqual(shell.run_interactive(lambda _: next(inputs)), 3)

    def test_exit_bad_argument(self):
        """exit с нечисловым аргументом - ошибка, работа продолжается."""
        shell, lines = make_shell()
        inputs = iter(["exit abc", "exit"])
        self.assertEqual(shell.run_interactive(lambda _: next(inputs)), 0)
        self.assertIn("exit: abc: numeric argument required", lines)

    def test_eof_finishes(self):
        """Конец ввода (Ctrl+D) завершает работу с кодом 0."""
        shell, _ = make_shell()

        def read(_):
            """Сымитировать конец ввода."""
            raise EOFError

        self.assertEqual(shell.run_interactive(read), 0)


if __name__ == "__main__":
    unittest.main()
