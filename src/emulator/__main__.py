"""Точка входа: python3 -m emulator [--vfs PATH] [--script PATH]."""

import sys

from emulator.config import debug_lines, parse_args
from emulator.errors import ShellError, ShellExit
from emulator.shell import Shell


def main(argv=None):
    """Запустить эмулятор и вернуть код завершения."""
    options = parse_args(argv)
    for line in debug_lines(options):
        print(line)
    shell = Shell()
    if options.script:
        try:
            shell.run_script(options.script)
        except ShellExit as stop:
            return stop.code
        except ShellError as error:
            print(f"emulator: {error}", file=sys.stderr)
            return 1
    return shell.run_interactive()


if __name__ == "__main__":
    sys.exit(main())
