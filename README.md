# Задание №1

Вариант 15

Разработать эмулятор для языка оболочки ОС. Необходимо сделать работу эмулятора как можно более похожей на работу в командной строке UNIX-подобной ОС.

## Этап 1. REPL

### Возможности

- Отображение приглашения к вводу вида `username@hostname:~$`.
- Парсинг строки ввода: команда + аргументы (разделяются пробелами).
- Поддержка команд-заглушек:
  - `ls` — выводит имя команды и список аргументов.
  - `cd` — выводит имя команды и список аргументов.
- Команда `exit` — завершает работу программы.

- Сообщения об ошибках:
  - `error: unknown command '<cmd>'` для неизвестных команд.

## Запуск

Требования: Python 3.10+.

Для запуска необходимо выполнить:

```
py repl.py
```

## Пример использования

![Скриншот работы](/screenshots/image.png)

## Этап 2. Конфигурация

### Возможности

- Указание пути к VFS (обязательный аргумент).
- Указание пути к стартовому скрипту (опциональный аргумент).
- Выполнение команд из скрипта с остановкой при первой ошибке.
- Запуск через скрипты Windows.

## Примеры .cmd скриптов

### Запуск только с VFS

```cmd
@echo off
python repl.py vfs.csv
pause
```

### Запуск с VFS и стартовым скриптом

```cmd
@echo off
python repl.py vfs.csv startup1.txt
pause
```

### Запуск без указания VFS (ошибка)

```cmd
@echo off
python repl.py
pause
```

# Пример стартового скрипта

```cmd
ls file1.txt
cd /home
hello
exit
```

## Этап 3. Виртуальная файловая система

### Возможности

- Загрузка структуры файлов и директорий из CSV-файла
- Все операции выполняются в памяти
- Команда `vfs-info`:
  - выводит имя VFS
  - выводит SHA-256 хеш исходного CSV-файла
- Проверка ошибок:
  - VFS файл не найден
  - Некорректный формат CSV
  - Путь не начинается с `/`
  - Неверный тип узла (не `file` и не `dir`)
  - Конфликт файл/директория
  - Некорректное содержимое base64
- Добавлены различные скрипты ОС для теста работы эмулятора

## Примеры csv файлов

### Минимальный

```csv
path,type,content
/,dir,
```

### Средний

```
path,type,content
/,dir,
/hello.txt,file,SGVsbG8gd29ybGQh
```

### Большой

```
path,type,content
/,dir,
/docs,dir,
/docs/readme.txt,file,UmVhZG1lIGZpbGU=
/bin,dir,
/bin/tool.sh,file,IyEvYmluL2Jhc2gKZWNobyAiUnVubmluZyB0b29sIg==
/bin/utils,dir,
/bin/utils/helper.sh,file,IyEvYmluL2Jhc2gKZWNobyAiSGVscGVyIHNjcmlwdCI=
```

## Примеры .cmd скриптов

### Запуск с VFS

```cmd
@echo off
echo Running emulator with big VFS...
py repl.py vfs_big.csv
```

### Запуск с VFS и стартовым скриптом

```cmd
@echo off
echo Running emulator with VFS and startup script...
py repl.py vfs_medium.csv startup.txt
```

### Запуск с некорректой VFS (ошибка)

```cmd
@echo off
echo Running emulator with invalid VFS...
py repl.py vfs_invalid_type.csv startup_invalid_vfs.txt
```

## Пример стартового скрипта

```txt
vfs-info
ls
cd /home
print
ls a b c
exit
```
