"""Output helpers: no-overwrite run folders, deterministic files, manifests."""
import csv
import hashlib
import json
import os
import platform
import re
from pathlib import Path


def validate_run_id(run_id: str) -> None:
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', run_id):
        raise ValueError('Run ID must contain only letters, numbers, dots, underscores, or hyphens')


def prepare_dirs(paths) -> list[Path]:
    """Preflight every destination, then create them. Nothing is created on failure."""
    paths = [Path(p).resolve() for p in paths]
    for i, p in enumerate(paths):
        for q in paths[i + 1:]:
            if p == q or p in q.parents or q in p.parents:
                raise ValueError('Destinations must be separate, non-nested directories')
    for p in paths:
        if p.exists():
            raise FileExistsError(f'Refusing to overwrite existing run: {p}')
    for p in paths:
        p.mkdir(parents=True, exist_ok=False)
    return paths


def relative(target: Path, base: Path) -> str:
    return Path(os.path.relpath(target, base)).as_posix()


def write_csv(path: Path, rows: list[dict]) -> None:
    with Path(path).open('w', newline='', encoding='utf-8') as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


def write_json(path: Path, obj) -> None:
    Path(path).write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')


def write_jsonl(path: Path, rows) -> None:
    with Path(path).open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row) + '\n')


def source_hashes(root: Path, extra=()) -> dict:
    files = sorted(Path(root, 'prehack').rglob('*.py')) + [Path(e).resolve() for e in extra]
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in files}


def base_manifest(root: Path, experiment: str, run_id: str, runner_file, **fields) -> dict:
    return {'schema_version': 1, 'experiment': experiment, 'run_id': run_id,
            'python': platform.python_version(),
            'source_sha256': source_hashes(root, [runner_file]), **fields}
