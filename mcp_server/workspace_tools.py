import os
import sys
import subprocess
import shutil
import fnmatch
from pathlib import Path
from typing import Optional, List, Dict, Any
from mcp_server.config import settings

def resolve_safe_path(relative_or_absolute: str) -> Path:
    '''Resolve path and ensure it is safely inside the configured workspace.'''
    base = settings.WORKSPACE_DIR.resolve()
    target = Path(relative_or_absolute)
    if not target.is_absolute():
        target = (base / target).resolve()
    else:
        target = target.resolve()
    
    # Path traversal check
    try:
        target.relative_to(base)
    except ValueError:
        raise ValueError(f'Access denied: Path \"{target}\" is outside workspace \"{base}\"')
    return target

def list_directory(rel_path: str = '.', recursive: bool = False, max_depth: int = 2) -> Dict[str, Any]:
    '''List files and folders within the workspace directory.'''
    target = resolve_safe_path(rel_path)
    if not target.exists():
        raise FileNotFoundError(f'Directory does not exist: {rel_path}')
    if not target.is_dir():
        raise NotADirectoryError(f'Path is not a directory: {rel_path}')

    items = []
    base = settings.WORKSPACE_DIR.resolve()

    def scan(current: Path, depth: int):
        if depth > max_depth and recursive:
            return
        try:
            for entry in current.iterdir():
                # Ignore .git internals unless requested
                if entry.name == '.git':
                    continue
                is_dir = entry.is_dir()
                size = None if is_dir else entry.stat().st_size
                rel = str(entry.relative_to(base)).replace('\\', '/')
                items.append({
                    'name': entry.name,
                    'path': rel,
                    'type': 'directory' if is_dir else 'file',
                    'size_bytes': size
                })
                if is_dir and recursive and depth < max_depth:
                    scan(entry, depth + 1)
        except PermissionError:
            pass

    scan(target, 1)
    return {
        'workspace': str(base),
        'directory': str(target.relative_to(base)).replace('\\', '/') if target != base else '.',
        'total_items': len(items),
        'items': items
    }

def read_file(rel_path: str, start_line: int = 1, end_line: int = -1) -> Dict[str, Any]:
    '''Read contents of a file within the workspace with optional line slice.'''
    target = resolve_safe_path(rel_path)
    if not target.exists():
        raise FileNotFoundError(f'File not found: {rel_path}')
    if not target.is_file():
        raise IsADirectoryError(f'Path is a directory, not a file: {rel_path}')

    with open(target, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    total_lines = len(lines)
    if start_line < 1:
        start_line = 1
    if end_line == -1 or end_line > total_lines:
        end_line = total_lines

    sliced_lines = lines[start_line - 1 : end_line]
    content = ''.join(sliced_lines)

    return {
        'path': rel_path,
        'total_lines': total_lines,
        'start_line': start_line,
        'end_line': end_line,
        'content': content
    }

def write_file(rel_path: str, content: str, overwrite: bool = True) -> Dict[str, Any]:
    '''Create or overwrite a file in the workspace.'''
    target = resolve_safe_path(rel_path)
    if target.exists() and not overwrite:
        raise FileExistsError(f'File already exists: {rel_path}')
    
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, 'w', encoding='utf-8') as f:
        f.write(content)

    return {
        'status': 'success',
        'path': rel_path,
        'bytes_written': len(content.encode('utf-8'))
    }

def edit_file(rel_path: str, target_snippet: str, replacement: str) -> Dict[str, Any]:
    '''Replace target_snippet with replacement in the specified file.'''
    target = resolve_safe_path(rel_path)
    if not target.exists():
        raise FileNotFoundError(f'File not found: {rel_path}')

    with open(target, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    if target_snippet not in content:
        raise ValueError(f'target_snippet not found in file: {rel_path}')

    new_content = content.replace(target_snippet, replacement, 1)
    with open(target, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return {
        'status': 'success',
        'path': rel_path,
        'message': 'Snippet replaced successfully'
    }

def delete_file(rel_path: str) -> Dict[str, Any]:
    '''Delete a file or empty directory in the workspace.'''
    target = resolve_safe_path(rel_path)
    if not target.exists():
        raise FileNotFoundError(f'Not found: {rel_path}')

    if target.is_dir():
        target.rmdir()
        msg = 'Directory removed'
    else:
        target.unlink()
        msg = 'File deleted'

    return {'status': 'success', 'path': rel_path, 'message': msg}

def search_files(query: str, rel_path: str = '.', case_sensitive: bool = False, extension: str = '') -> Dict[str, Any]:
    '''Search file names or contents for a given query string.'''
    base = resolve_safe_path(rel_path)
    matches = []
    
    for root, dirs, files in os.walk(base):
        if '.git' in dirs:
            dirs.remove('.git')
        if 'node_modules' in dirs:
            dirs.remove('node_modules')
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')

        for file in files:
            if extension and not file.endswith(extension):
                continue
            file_path = Path(root) / file
            rel = str(file_path.relative_to(settings.WORKSPACE_DIR)).replace('\\', '/')
            
            # Check name
            name_match = (query in file) if case_sensitive else (query.lower() in file.lower())
            
            # Check content
            content_matches = []
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        matched = (query in line) if case_sensitive else (query.lower() in line.lower())
                        if matched:
                            content_matches.append({'line': line_num, 'text': line.strip()})
                            if len(content_matches) >= 10:
                                break
            except Exception:
                pass

            if name_match or content_matches:
                matches.append({
                    'file': rel,
                    'name_match': name_match,
                    'content_matches': content_matches
                })
            if len(matches) >= 50:
                break

    return {'query': query, 'total_matches': len(matches), 'results': matches}

def execute_command(command: str, timeout: Optional[int] = None) -> Dict[str, Any]:
    '''Execute a shell command (PowerShell on Windows) within the workspace directory.'''
    if not settings.ENABLE_COMMAND_EXECUTION:
        raise PermissionError('Command execution is disabled in server configuration.')

    t = timeout or settings.COMMAND_TIMEOUT_SECONDS
    cwd = settings.WORKSPACE_DIR
    
    try:
        proc = subprocess.run(
            ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', command],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=t,
            shell=False
        )
        return {
            'command': command,
            'exit_code': proc.returncode,
            'stdout': proc.stdout,
            'stderr': proc.stderr,
            'timed_out': False
        }
    except subprocess.TimeoutExpired:
        return {
            'command': command,
            'exit_code': -1,
            'stdout': '',
            'stderr': f'Command timed out after {t} seconds.',
            'timed_out': True
        }
    except Exception as e:
        return {
            'command': command,
            'exit_code': -1,
            'stdout': '',
            'stderr': str(e),
            'timed_out': False
        }

def get_workspace_info() -> Dict[str, Any]:
    '''Get workspace metadata, environment details, and disk info.'''
    ws = settings.WORKSPACE_DIR
    total, used, free = shutil.disk_usage(ws)
    return {
        'workspace_path': str(ws),
        'exists': ws.exists(),
        'disk_free_gb': round(free / (1024 ** 3), 2),
        'disk_total_gb': round(total / (1024 ** 3), 2),
        'python_version': sys.version,
        'command_execution_enabled': settings.ENABLE_COMMAND_EXECUTION,
        'ponytail_mode': settings.PONYTAIL_MODE
    }

def switch_workspace(new_path: str) -> Dict[str, Any]:
    '''Switch the active workspace directory to a new folder on the computer.'''
    target = Path(new_path).resolve()
    if not target.exists():
        raise FileNotFoundError(f'Thư mục không tồn tại: {new_path}')
    if not target.is_dir():
        raise NotADirectoryError(f'Đường dẫn không phải thư mục: {new_path}')

    settings.WORKSPACE_DIR = target
    return {
        'status': 'success',
        'current_workspace': str(target),
        'message': f'Đã chuyển thành công workspace sang: {target}. Mọi lệnh và thao tác tệp tiếp theo sẽ thực hiện tại đây.'
    }

def list_available_drives() -> Dict[str, Any]:
    '''List available drives and common user folders (Desktop, Documents, Downloads).'''
    import string
    drives = []
    for letter in string.ascii_uppercase:
        dp = Path(f'{letter}:/')
        if dp.exists():
            drives.append(f'{letter}:/')

    home = Path.home()
    quick_paths = {
        'Desktop': str(home / 'Desktop'),
        'Documents': str(home / 'Documents'),
        'Downloads': str(home / 'Downloads'),
        'Home': str(home)
    }
    return {
        'drives': drives,
        'quick_paths': {k: v for k, v in quick_paths.items() if Path(v).exists()},
        'current_workspace': str(settings.WORKSPACE_DIR)
    }

