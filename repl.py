import os
import sys
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

def run_command(command, args):
    if command == "exit":
        return False
    elif command == "ls":
        print(f"command: {command}, args: {args}")
    elif command == "cd":
        print(f"command: {command}, args: {args}")
    else:
        print(f"error: unknown command '{command}'")
        return False
    return True

def run_script(script_path):
    if not os.path.exists(script_path):
        print(f"error: startup script '{script_path}' not found")
        return
    with open(script_path, "r") as script:
        for line in script:
            line = line.strip()
            print(get_prompt() + line)
            command, args = parse_command(line)
            if command is None:
                continue
            keep_running = run_command(command, args)
            if not keep_running:
                sys.exit(0)

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
        keep_running = run_command(command, args)
        if not keep_running:
            break

def main():
    vfs_path = None
    startup_script = None

    if len(sys.argv) > 1:
        vfs_path = sys.argv[1]
    if len(sys.argv) > 2:
        startup_script = sys.argv[2]

    if not vfs_path:
        print("error: VFS path is required")
        return

    print("VFS path:", vfs_path)
    print("Startup script:", startup_script if startup_script else "None")

    if startup_script:
        run_script(startup_script)

    repl()

if __name__ == "__main__":
    main()

