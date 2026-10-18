"""Точка входа: python3 -m emulator."""

import sys

from emulator.shell import Shell


def main():
    """Запустить эмулятор и вернуть код завершения."""
    return Shell().run_interactive()


if __name__ == "__main__":
    sys.exit(main())
