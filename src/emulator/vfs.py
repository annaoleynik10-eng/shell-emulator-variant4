"""Виртуальная файловая система (VFS), которая хранится в памяти.

Источник VFS - ZIP-архив. Архив читается целиком в память и не
распаковывается на диск. Содержимое файлов хранится в виде байтов;
двоичные файлы при выводе показываются в кодировке base64.
"""

import base64
import zipfile

from emulator.errors import ShellError

ROOT_SYMBOL = "~"
SEPARATOR = "/"
CURRENT_DIR = "."
PARENT_DIR = ".."
SKIPPED_PREFIXES = ("__MACOSX/",)
SKIPPED_NAMES = (".DS_Store",)


class Node:
    """Узел VFS: файл или каталог."""

    def __init__(self, name, is_dir, owner, data=b""):
        """Создать узел с именем, типом, владельцем и содержимым."""
        self.name = name
        self.is_dir = is_dir
        self.owner = owner
        self.data = data
        self.children = {}

    def size(self):
        """Вернуть размер файла в байтах (у каталога - 0)."""
        return len(self.data)

    def text(self):
        """Вернуть содержимое файла как текст.

        Если файл не является текстом UTF-8, он считается двоичным
        и возвращается в виде строки base64.
        """
        try:
            return self.data.decode("utf-8")
        except UnicodeDecodeError:
            return base64.b64encode(self.data).decode("ascii")


class VFS:
    """Дерево каталогов и файлов в памяти."""

    def __init__(self, owner, source=None):
        """Создать пустую VFS с корневым каталогом."""
        self.root = Node("", True, owner)
        self.owner = owner
        self.source = source

    @classmethod
    def from_zip(cls, path, owner):
        """Загрузить VFS из ZIP-архива, не распаковывая его на диск."""
        vfs = cls(owner, source=path)
        try:
            with zipfile.ZipFile(path) as archive:
                for info in archive.infolist():
                    if is_skipped(info.filename):
                        continue
                    data = b"" if info.is_dir() else archive.read(info)
                    vfs.add(info.filename, info.is_dir(), data)
        except (OSError, zipfile.BadZipFile) as error:
            raise ShellError(f"cannot load VFS from {path}: {error}") \
                from error
        return vfs

    def add(self, path, is_dir, data=b""):
        """Добавить файл или каталог, создав недостающих родителей."""
        parts = [part for part in path.split(SEPARATOR) if part]
        node = self.root
        for name in parts[:-1]:
            node = node.children.setdefault(
                name, Node(name, True, self.owner))
        if not parts:
            return
        last = parts[-1]
        if is_dir:
            node.children.setdefault(last, Node(last, True, self.owner))
        else:
            node.children[last] = Node(last, False, self.owner, data)

    def resolve(self, cwd, path):
        """Преобразовать путь в список имён от корня.

        Поддерживаются абсолютные пути (/a, ~/a), относительные
        пути, а также специальные имена . и ..
        """
        if path.startswith(SEPARATOR) or path.startswith(ROOT_SYMBOL):
            parts = []
            path = path.lstrip(ROOT_SYMBOL)
        else:
            parts = list(cwd)
        for name in path.split(SEPARATOR):
            if name in ("", CURRENT_DIR):
                continue
            if name == PARENT_DIR:
                if parts:
                    parts.pop()
            else:
                parts.append(name)
        return parts

    def get(self, parts):
        """Найти узел по списку имён. Вернуть None, если его нет."""
        node = self.root
        for name in parts:
            if not node.is_dir or name not in node.children:
                return None
            node = node.children[name]
        return node

    def count(self):
        """Вернуть кортеж (число каталогов, число файлов) без корня."""
        dirs = files = 0
        stack = [self.root]
        while stack:
            node = stack.pop()
            for child in node.children.values():
                if child.is_dir:
                    dirs += 1
                    stack.append(child)
                else:
                    files += 1
        return dirs, files


def is_skipped(name):
    """Проверить, является ли запись архива служебной (мусор macOS)."""
    base = name.rstrip(SEPARATOR).split(SEPARATOR)[-1]
    return name.startswith(SKIPPED_PREFIXES) or base in SKIPPED_NAMES
