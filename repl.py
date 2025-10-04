import os
import sys
import socket
import csv
import base64
import hashlib

def make_dir_node():
    return {"type": "dir", "children": {}}

def make_file_node(content_bytes: bytes):
    return {"type": "file", "content": content_bytes}

def get_prompt():
    username = os.getenv("USERNAME") or os.getenv("USER") or "user"
    hostname = socket.gethostname()
    return f"{username}@{hostname}:~$ "

def parse_command(line: str):
    parts = line.strip().split()
    if not parts:
        return None, []
    return parts[0], parts[1:]

def compute_sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()

def load_vfs_from_csv(path: str):
    if not os.path.exists(path):
        print(f"error: VFS file not found: {path}")
        return None, None, None

    with open(path, "rb") as bf:
        raw = bf.read()

    sha256 = compute_sha256_bytes(raw)
    vfs_name = os.path.basename(path)

    text = raw.decode("utf-8")
    
    root = make_dir_node()

    reader = csv.reader(text.splitlines())
    first_row = None
    rows = []
    for i, row in enumerate(reader):
        if not row or all(cell.strip() == "" for cell in row):
            continue
        if first_row is None:
            first_row = row
        rows.append(row)

    if first_row and len(first_row) >= 2 and first_row[0].lower() == "path" and first_row[1].lower() == "type":
        rows = rows[1:]

    for row_no, row in enumerate(rows, start=1):
        if len(row) < 2:
            print(f"error: invalid VFS format at CSV row {row_no}: expected at least 2 columns (path,type)")
            return None, None, None

        path_field = row[0].strip()
        type_field = row[1].strip().lower()
        content_field = row[2].strip() if len(row) >= 3 else ""

        if not path_field.startswith("/"):
            print(f"error: invalid VFS path at CSV row {row_no}: path must start with '/' -> {path_field}")
            return None, None, None

        if type_field not in ("file", "dir"):
            print(f"error: invalid VFS type at CSV row {row_no}: must be 'file' or 'dir' -> {type_field}")
            return None, None, None

        components = [comp for comp in path_field.split("/") if comp != ""]

        node = root
        for idx, comp in enumerate(components):
            is_last = (idx == len(components) - 1)
            if is_last:
                if type_field == "dir":
                    existing = node["children"].get(comp)
                    if existing and existing["type"] == "file":
                        print(f"error: path conflict at CSV row {row_no}: {path_field} already exists as file")
                        return None, None, None
                    if not existing:
                        node["children"][comp] = make_dir_node()
                else:
                    existing = node["children"].get(comp)
                    if existing and existing["type"] == "dir":
                        print(f"error: path conflict at CSV row {row_no}: {path_field} already exists as dir")
                        return None, None, None
                    if content_field == "":
                        file_bytes = b""
                    else:
                        try:
                            file_bytes = base64.b64decode(content_field, validate=True)
                        except Exception as e:
                            print(f"error: invalid base64 content at CSV row {row_no}: {e}")
                            return None, None, None
                    node["children"][comp] = make_file_node(file_bytes)
            else:
                existing = node["children"].get(comp)
                if existing:
                    if existing["type"] != "dir":
                        print(f"error: path conflict at CSV row {row_no}: {comp} expected to be dir in path {path_field}")
                        return None, None, None
                    node = existing
                else:
                    newdir = make_dir_node()
                    node["children"][comp] = newdir
                    node = newdir

    return vfs_name, sha256, root


def cmd_vfs_info(vfs_name, vfs_hash):
    print(f"VFS name: {vfs_name}")
    print(f"SHA-256: {vfs_hash}")

def run_command(command, args, vfs_context):
    if command == "exit":
        sys.exit(0)
    elif command == "ls":
        print(f"command: {command}, args: {args}")
    elif command == "cd":
        print(f"command: {command}, args: {args}")
    elif command == "vfs-info":
        cmd_vfs_info(vfs_context["vfs_name"], vfs_context["vfs_hash"])
    else:
        print(f"error: unknown command '{command}'")
        return False
    return True

def run_script(script_path, vfs_context):
    if not os.path.exists(script_path):
        print(f"error: startup script '{script_path}' not found")
        return
    with open(script_path, "r") as script:
        for line in script:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            print(get_prompt() + line)
            command, args = parse_command(line)
            if command is None:
                continue
            keep_running = run_command(command, args, vfs_context)
            if not keep_running:
                return


def repl(vfs_context):
    while True:
        try:
            line = input(get_prompt())
        except KeyboardInterrupt:
            print()
            continue

        command, args = parse_command(line)
        if command is None:
            continue
        run_command(command, args, vfs_context)

def main():
    vfs_path = None
    startup_script = None

    if len(sys.argv) > 1:
        vfs_path = sys.argv[1]
    if len(sys.argv) > 2:
        startup_script = sys.argv[2]

    if not vfs_path:
        print("error: VFS path is required")
        input("Press Enter to exit...")
        return


    vfs_name, vfs_hash, vfs_root = load_vfs_from_csv(vfs_path)
    if vfs_name is None:
        input("Press Enter to exit...")
        return

    vfs_context = {
        "vfs_name": vfs_name,
        "vfs_hash": vfs_hash,
        "vfs_root": vfs_root,
        "cwd": []  
    }

    print("VFS path:", vfs_path)
    print("Startup script:", startup_script if startup_script else "None")

    if startup_script:
        run_script(startup_script, vfs_context)

    repl(vfs_context)

if __name__ == "__main__":
    main()
