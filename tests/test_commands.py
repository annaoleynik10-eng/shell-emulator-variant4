"""Тесты этапа 4: команды ls, cd, uniq, find, rev."""

import unittest

from emulator.shell import Shell
from emulator.vfs import VFS


def make_shell():
    """Создать оболочку с небольшой VFS и списком для вывода."""
    vfs = VFS("anya")
    vfs.add("docs/log.txt", False, b"a\na\nb\na\n")
    vfs.add("docs/deep/x.md", False, b"abc\n")
    vfs.add("readme.txt", False, b"hello\n")
    lines = []
    return Shell(output=lines.append, vfs=vfs), lines


class LsCdTest(unittest.TestCase):
    """Проверки ls и cd."""

    def test_ls_root(self):
        """ls выводит имена в алфавитном порядке."""
        shell, lines = make_shell()
        shell.execute("ls")
        self.assertEqual(lines, ["docs  readme.txt"])

    def test_ls_long(self):
        """ls -l показывает тип, владельца и размер."""
        shell, lines = make_shell()
        shell.execute("ls -l readme.txt")
        self.assertEqual(lines, ["-rw-r--r-- anya          6 readme.txt"])

    def test_cd_changes_prompt(self):
        """cd меняет текущий каталог и приглашение."""
        shell, _ = make_shell()
        self.assertTrue(shell.execute("cd docs/deep"))
        self.assertEqual(shell.cwd_display(), "~/docs/deep")
        self.assertTrue(shell.execute("cd"))
        self.assertEqual(shell.cwd, [])

    def test_cd_errors(self):
        """cd в файл или в несуществующий путь - ошибка."""
        shell, lines = make_shell()
        self.assertFalse(shell.execute("cd readme.txt"))
        self.assertFalse(shell.execute("cd nope"))
        self.assertEqual(lines, [
            "cd: readme.txt: Not a directory",
            "cd: nope: No such file or directory",
        ])


class TextCommandsTest(unittest.TestCase):
    """Проверки uniq и rev."""

    def test_uniq_modes(self):
        """uniq, uniq -c и uniq -d."""
        shell, lines = make_shell()
        shell.execute("uniq docs/log.txt")
        shell.execute("uniq -c docs/log.txt")
        shell.execute("uniq -d docs/log.txt")
        self.assertEqual(lines, [
            "a\nb\na",
            "      2 a\n      1 b\n      1 a",
            "a",
        ])

    def test_rev(self):
        """rev переворачивает строки файла."""
        shell, lines = make_shell()
        shell.execute("rev readme.txt docs/deep/x.md")
        self.assertEqual(lines, ["olleh\ncba"])

    def test_rev_directory(self):
        """rev каталога - ошибка."""
        shell, lines = make_shell()
        self.assertFalse(shell.execute("rev docs"))
        self.assertEqual(lines, ["rev: docs: Is a directory"])


class FindTest(unittest.TestCase):
    """Проверки find."""

    def test_find_all(self):
        """find без аргументов обходит всё дерево от текущего каталога."""
        shell, lines = make_shell()
        shell.execute("cd docs")
        shell.execute("find")
        self.assertEqual(lines, [".\n./deep\n./deep/x.md\n./log.txt"])

    def test_find_name_and_type(self):
        """find с -name (в кавычках) и -type."""
        shell, lines = make_shell()
        shell.execute('find / -name "*.txt"')
        shell.execute("find / -type d")
        self.assertEqual(lines, [
            "/docs/log.txt\n/readme.txt",
            "/\n/docs\n/docs/deep",
        ])

    def test_find_errors(self):
        """Неизвестный предикат и отсутствующее значение."""
        shell, lines = make_shell()
        self.assertFalse(shell.execute("find / -size 1"))
        self.assertFalse(shell.execute("find / -name"))
        self.assertEqual(len(lines), 2)


if __name__ == "__main__":
    unittest.main()
