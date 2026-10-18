"""Тесты этапа 2: параметры командной строки и стартовый скрипт."""

import os
import tempfile
import unittest

from emulator.config import debug_lines, parse_args
from emulator.errors import ShellError, ShellExit
from emulator.shell import Shell


def write_script(text):
    """Записать текст во временный файл и вернуть путь к нему."""
    handle, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(handle, "w", encoding="utf-8") as file:
        file.write(text)
    return path


class ConfigTest(unittest.TestCase):
    """Проверки разбора параметров."""

    def test_all_options(self):
        """Оба параметра попадают в настройки и в отладочный вывод."""
        options = parse_args(["--vfs", "a.zip", "--script", "s.txt"])
        self.assertEqual(
            debug_lines(options),
            ["[debug] vfs = a.zip", "[debug] script = s.txt"],
        )

    def test_defaults(self):
        """Без параметров значения равны None."""
        options = parse_args([])
        self.assertIsNone(options.vfs)
        self.assertIsNone(options.script)


class ScriptTest(unittest.TestCase):
    """Проверки выполнения стартового скрипта."""

    def test_errors_are_skipped(self):
        """Ошибочные строки пропускаются, выполнение продолжается."""
        lines = []
        shell = Shell(output=lines.append)
        path = write_script("# comment\n\nfoo\nexit 1 2\nls\n")
        self.addCleanup(os.remove, path)
        self.assertEqual(shell.run_script(path), 2)
        self.assertIn("foo: command not found", lines)
        self.assertEqual(lines[-1], f"{shell.prompt()}ls")
        self.assertTrue(lines[0].endswith("$ foo"))

    def test_exit_stops_script(self):
        """exit в скрипте останавливает выполнение."""
        shell = Shell(output=lambda _: None)
        path = write_script("exit 7\nls\n")
        self.addCleanup(os.remove, path)
        with self.assertRaises(ShellExit) as context:
            shell.run_script(path)
        self.assertEqual(context.exception.code, 7)

    def test_missing_script(self):
        """Несуществующий скрипт вызывает ShellError."""
        shell = Shell(output=lambda _: None)
        with self.assertRaises(ShellError):
            shell.run_script("/no/such/file.txt")


if __name__ == "__main__":
    unittest.main()
