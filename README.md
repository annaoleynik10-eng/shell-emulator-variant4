# Эмулятор командной оболочки (вариант 4)

Практическая работа № 1 по дисциплине «Конфигурационное управление».
Выполнила: Быстрова Анна Сергеевна, группа УНБО-04-25.

## 1. Общее описание

Консольное приложение (CLI), которое имитирует работу командной строки
UNIX-подобной ОС. Файловая система эмулятора виртуальная (VFS): она
загружается из ZIP-архива в память, и все изменения происходят
только в памяти.

Язык реализации: Python 3.8+, только стандартная библиотека.

Структура репозитория:

```
src/emulator/
    __main__.py   точка входа, запуск эмулятора
    config.py     параметры командной строки
    shell.py      приглашение, REPL, выполнение стартового скрипта
    parser.py     разбор строки на команду и аргументы
    commands.py   реализация всех команд
    vfs.py        виртуальная файловая система в памяти
    errors.py     исключения ShellError и ShellExit
    build_vfs.py  сборка ZIP-образа VFS из папки
tests/
    test_*.py     модульные тесты (unittest)
    sh/           скрипты ОС для проверки каждого этапа
    startup/      стартовые скрипты эмулятора
    vfs/          тестовые VFS в виде папок: minimal, several, deep
run.sh            скрипт запуска
```

## 2. Функции и настройки

### Параметры командной строки

| Параметр | Назначение |
|---|---|
| `--vfs PATH` | путь к ZIP-архиву с VFS; без него VFS пустая |
| `--script PATH` | путь к стартовому скрипту |
| `-h`, `--help` | справка по параметрам |

При запуске эмулятор печатает отладочный вывод всех параметров:
`[debug] vfs = ...`, `[debug] script = ...`.

### Приглашение

Строится по реальным данным ОС: `пользователь@хост:каталог$`.
Корень VFS обозначается `~`, например `anya@macbook:~/home/anya$`.

### Стартовый скрипт

- Команды выполняются по очереди, каждая печатается вместе с
  приглашением, как будто её ввёл пользователь.
- Пустые строки и комментарии (`#`) пропускаются.
- Строки с ошибками пропускаются, выполнение продолжается.
- Если в скрипте нет `exit`, после него начинается диалог.

### VFS

- Источник - ZIP-архив. Он читается модулем `zipfile` в память и не
  распаковывается на диск.
- Текстовые файлы читаются как UTF-8, двоичные выводятся в base64.
- Если в корне есть файл `motd`, он выводится при старте.
- Служебные файлы macOS (`__MACOSX`, `.DS_Store`) пропускаются.

### Команды

| Команда | Описание |
|---|---|
| `ls [-l] [путь ...]` | содержимое каталога; `-l` - права, владелец, размер |
| `cd [путь]` | смена каталога; без аргумента - в корень |
| `uniq [-c] [-d] файл` | убрать повторы подряд; `-c` - число повторов, `-d` - только повторы |
| `find [путь] [-name шаблон] [-type f\|d]` | рекурсивный поиск |
| `rev файл [файл ...]` | перевернуть каждую строку |
| `chown [-R] владелец путь [путь ...]` | сменить владельца (в памяти); `-R` - рекурсивно |
| `help [команда ...]` | список команд с описанием |
| `exit [код]` | выход с кодом (по умолчанию 0) |
| `vfs-info` | служебная: источник VFS, число каталогов и файлов |

Пути бывают абсолютные (`/etc`, `~/etc`) и относительные, также
поддерживаются `.` и `..`. Кавычки работают как в настоящей
оболочке: `find / -name "*.txt"`.

Ошибки выводятся в стиле bash: `cd: nowhere: No such file or directory`,
`foo: command not found`.

## 3. Сборка, запуск и тесты

Сборка не требуется, нужен только Python 3.

```sh
chmod +x run.sh tests/sh/*.sh   # один раз: разрешить запуск скриптов

./run.sh                                  # диалоговый режим
./run.sh --vfs vfs.zip --script s.txt     # с VFS и стартовым скриптом

# ZIP-образ VFS из папки:
PYTHONPATH=src python3 -m emulator.build_vfs tests/vfs/deep deep.zip

# модульные тесты:
PYTHONPATH=src python3 -m unittest discover -s tests -t .

# проверка этапов скриптами ОС:
./tests/sh/stage2.sh   # параметры командной строки
./tests/sh/stage3.sh   # варианты VFS: minimal, several, deep
./tests/sh/stage4.sh   # ls, cd, uniq, find, rev
./tests/sh/stage5.sh   # chown, help
```

Архивы в репозитории не хранятся: скрипты `tests/sh` собирают их во
временной папке из `tests/vfs` и удаляют после проверки.

## 4. Примеры использования

```
$ ./run.sh --vfs deep.zip
[debug] vfs = deep.zip
[debug] script = None
=== Добро пожаловать в глубокую VFS ===
Уровней вложенности: 4
anya@macbook:~$ ls
bin  etc  home  motd  var
anya@macbook:~$ cd home/anya
anya@macbook:~/home/anya$ ls -l docs
-rw-r--r-- anya         39 lecture.txt
-rw-r--r-- anya         22 todo.txt
anya@macbook:~/home/anya$ cd
anya@macbook:~$ uniq -c var/log/system.log
      3 boot ok
      1 disk warning
      1 boot ok
anya@macbook:~$ rev etc/hostname
tsoh-rotalume
anya@macbook:~$ find / -name "*.txt"
/home/anya/docs/lecture.txt
/home/anya/docs/todo.txt
anya@macbook:~$ chown -R guest home
anya@macbook:~$ ls -l
drwxr-xr-x anya          0 bin
drwxr-xr-x anya          0 etc
drwxr-xr-x guest         0 home
-rw-r--r-- anya        105 motd
drwxr-xr-x anya          0 var
anya@macbook:~$ cd nowhere
cd: nowhere: No such file or directory
anya@macbook:~$ foo
foo: command not found
anya@macbook:~$ exit
```
