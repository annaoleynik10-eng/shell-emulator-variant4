"""Тесты этапа 5: команды chown и help."""

import unittest

from emulator.commands import COMMANDS
from emulator.shell import Shell
from emulator.vfs import VFS


def make_shell():
    """Создать оболочку с небольшой VFS и списком для вывода."""
    vfs = VFS("root")
    vfs.add("home/anya/notes.txt", False, b"x")
    vfs.add("etc/passwd", False, b"root")
    lines = []
    return Shell(output=lines.append, vfs=vfs), lines


class ChownTest(unittest.TestCase):
    """Проверки chown."""

    def test_single_file(self):
        """chown меняет владельца одного файла."""
        shell, _ = make_shell()
        self.assertTrue(shell.execute("chown anya etc/passwd"))
        self.assertEqual(shell.vfs.get(["etc", "passwd"]).owner, "anya")
        self.assertEqual(shell.vfs.get(["etc"]).owner, "root")

    def test_recursive(self):
        """chown -R меняет владельца всего поддерева."""
        shell, _ = make_shell()
        self.assertTrue(shell.execute("chown -R guest home"))
        node = shell.vfs.get(["home", "anya", "notes.txt"])
        self.assertEqual(node.owner, "guest")

    def test_errors_do_not_change_vfs(self):
        """При ошибке в одном из путей ничего не меняется."""
        shell, lines = make_shell()
        self.assertFalse(shell.execute("chown anya etc/passwd nope"))
        self.assertFalse(shell.execute("chown Bad! etc/passwd"))
        self.assertFalse(shell.execute("chown anya"))
        self.assertEqual(shell.vfs.get(["etc", "passwd"]).owner, "root")
        self.assertEqual(lines, [
            "chown: nope: No such file or directory",
            "chown: invalid user: 'Bad!'",
            "chown: missing operand",
        ])


class HelpTest(unittest.TestCase):
    """Проверки help."""

    def test_lists_all_commands(self):
        """help выводит по строке на каждую команду."""
        shell, lines = make_shell()
        shell.execute("help")
        self.assertEqual(len(lines[0].splitlines()), len(COMMANDS))

    def test_unknown_topic(self):
        """help для неизвестной команды - ошибка."""
        shell, lines = make_shell()
        self.assertFalse(shell.execute("help nope"))
        self.assertEqual(lines, ["help: no help topics match 'nope'"])


if __name__ == "__main__":
    unittest.main()
