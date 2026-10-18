"""Тесты этапа 3: загрузка VFS из ZIP и работа с путями."""

import base64
import io
import unittest
import zipfile

from emulator.errors import ShellError
from emulator.shell import Shell
from emulator.vfs import VFS

BINARY = b"\x00\x01\xff"


def make_zip(files):
    """Собрать ZIP в памяти из словаря {путь: байты}."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    buffer.seek(0)
    return buffer


def sample_vfs():
    """VFS с тремя уровнями вложенности, двоичным файлом и motd."""
    return VFS.from_zip(make_zip({
        "motd": "Hello!\n".encode(),
        "a/b/c/deep.txt": b"deep",
        "a/bin.dat": BINARY,
        "__MACOSX/a/._bin.dat": b"junk",
        "a/.DS_Store": b"junk",
    }), "anya")


class VfsLoadTest(unittest.TestCase):
    """Проверки загрузки VFS."""

    def test_structure(self):
        """Каталоги создаются автоматически, мусор macOS пропускается."""
        vfs = sample_vfs()
        self.assertEqual(vfs.count(), (3, 3))
        self.assertTrue(vfs.get(["a", "b", "c"]).is_dir)

    def test_binary_as_base64(self):
        """Двоичный файл выводится в base64."""
        node = sample_vfs().get(["a", "bin.dat"])
        self.assertEqual(node.text(), base64.b64encode(BINARY).decode())

    def test_bad_archive(self):
        """Повреждённый архив вызывает ShellError."""
        with self.assertRaises(ShellError):
            VFS.from_zip(io.BytesIO(b"not a zip"), "anya")

    def test_motd(self):
        """Сообщение motd выводится из корня VFS."""
        lines = []
        Shell(output=lines.append, vfs=sample_vfs()).show_motd()
        self.assertEqual(lines, ["Hello!"])


class ResolveTest(unittest.TestCase):
    """Проверки разбора путей."""

    def setUp(self):
        """Создать VFS для тестов."""
        self.vfs = sample_vfs()

    def test_relative_and_parent(self):
        """Относительный путь с .. и . от текущего каталога."""
        self.assertEqual(
            self.vfs.resolve(["a", "b"], "../b/./c"), ["a", "b", "c"])

    def test_absolute(self):
        """Пути от / и от ~ ведут в корень VFS."""
        self.assertEqual(self.vfs.resolve(["a"], "/a/b"), ["a", "b"])
        self.assertEqual(self.vfs.resolve(["a"], "~"), [])

    def test_parent_of_root(self):
        """.. в корне остаётся в корне."""
        self.assertEqual(self.vfs.resolve([], "../.."), [])

    def test_missing(self):
        """Несуществующий путь даёт None."""
        self.assertIsNone(self.vfs.get(["a", "zzz"]))


if __name__ == "__main__":
    unittest.main()
