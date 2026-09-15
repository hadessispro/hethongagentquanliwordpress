import os
import re
from pathlib import Path
from typing import Dict, Any, Optional
from mcp_server.config import settings

MODES = ['lite', 'full', 'ultra']
DEFAULT_MODE = 'full'

def normalize_mode(mode: Optional[str]) -> str:
    m = (mode or '').lower().strip()
    return m if m in MODES else DEFAULT_MODE

def get_ponytail_instructions(mode: Optional[str] = None) -> Dict[str, str]:
    '''Load and build Ponytail lazy-senior-dev instructions from ponytail repo or fallback.'''
    eff_mode = normalize_mode(mode or settings.PONYTAIL_MODE)
    skill_file = settings.PONYTAIL_DIR / 'skills' / 'ponytail' / 'SKILL.md'

    instructions = ''
    if skill_file.exists():
        try:
            raw = skill_file.read_text(encoding='utf-8')
            # Strip frontmatter
            body = re.sub(r'^---[\s\S]*?---\s*', '', raw)
            # Filter mode-specific rows/examples
            lines = []
            for line in body.splitlines():
                table_match = re.match(r'^\|\s*\*\*(.+?)\*\*\s*\|', line)
                if table_match:
                    lbl = table_match.group(1).strip().lower()
                    if lbl in MODES and lbl != eff_mode:
                        continue
                ex_match = re.match(r'^-\s*([^:]+):\s*"', line)
                if ex_match:
                    lbl = ex_match.group(1).strip().lower()
                    if lbl in MODES and lbl != eff_mode:
                        continue
                lines.append(line)
            instructions = f'PONYTAIL MODE ACTIVE — level: {eff_mode}\n\n' + '\n'.join(lines)
        except Exception:
            pass

    if not instructions:
        instructions = (
            f'PONYTAIL MODE ACTIVE — level: {eff_mode}\n\n'
            'You are a lazy senior developer. Lazy means efficient, not careless. The best code is the code never written.\n\n'
            '## The ladder\n'
            'Before any code, stop at the first rung that holds:\n'
            '1. Does this need to be built at all? (YAGNI)\n'
            '2. Does it already exist in this codebase? Reuse what is already here.\n'
            '3. Does the standard library do this? Use it.\n'
            '4. Does a native platform feature cover it? Use it.\n'
            '5. Does an already-installed dependency solve it? Use it.\n'
            '6. Can this be one line? Make it one line.\n'
            '7. Only then: write the minimum code that works.\n\n'
            '## Output\n'
            'Code first. Then at most three short lines: what was skipped, when to add it.\n'
            'No unrequested abstractions. Boring over clever. Fewest files possible.'
        )

    return {'mode': eff_mode, 'instructions': instructions}

def audit_workspace(rel_path: str = '.') -> Dict[str, Any]:
    '''Audit code files in workspace using Ponytail minimalism criteria.'''
    from mcp_server.workspace_tools import resolve_safe_path
    target = resolve_safe_path(rel_path)

    findings = []
    total_files = 0

    for root, dirs, files in os.walk(target):
        if any(ignored in root for ignored in ['.git', 'node_modules', '__pycache__', '.venv']):
            continue
        for file in files:
            if not file.endswith(('.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.html')):
                continue
            total_files += 1
            fp = Path(root) / file
            rel = str(fp.relative_to(settings.WORKSPACE_DIR)).replace('\\', '/')
            
            try:
                lines = fp.read_text(encoding='utf-8', errors='ignore').splitlines()
                # Check for large files
                if len(lines) > 400:
                    findings.append({
                        'file': rel,
                        'issue': 'File size warning',
                        'detail': f'{len(lines)} lines. Consider simplifying or splitting if multiple responsibilities exist.'
                    })
                # Check for unnecessary abstract classes or excessive boilerplate
                todo_count = sum(1 for line in lines if 'TODO' in line or 'FIXME' in line)
                if todo_count > 3:
                    findings.append({
                        'file': rel,
                        'issue': 'Tech debt indicators',
                        'detail': f'{todo_count} TODO/FIXME markers found.'
                    })
            except Exception:
                pass

    return {
        'total_scanned_files': total_files,
        'total_findings': len(findings),
        'findings': findings,
        'advice': 'Apply Ponytail Decision Ladder: Delete unused files, avoid speculative abstractions, use stdlib.'
    }
