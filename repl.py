import os
import socket

def get_prompt():
    username = os.getenv("USERNAME") or os.getenv("USER") or "user"
    hostname = socket.gethostname()
    return f"{username}@{hostname}:~$ "

def parse_command(line: str):
    parts = line.strip().split()
    if not parts:
        return None, []
    return parts[0], parts[1:]

def repl():
    while True:
        try:
            line = input(get_prompt()) 
        except KeyboardInterrupt:
            print() 
            continue

        command, args = parse_command(line)
        if command is None:
            continue
        if command == "exit":
            break
        elif command == "ls":
            print(f"command: {command}, args: {args}")
        elif command == "cd":
            print(f"command: {command}, args: {args}")
        else:
            print(f"error: unknown command '{command}'")


repl()
