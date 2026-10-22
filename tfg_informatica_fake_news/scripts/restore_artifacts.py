"""Restore versioned gzip artefacts, checking bytes and preserving existing files."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def project_file(root: Path, relative: str) -> Path:
    name = PurePosixPath(relative)
    if name.is_absolute() or '..' in name.parts or '\\' in relative or ':' in relative:
        raise ValueError(f'Ruta fuera del proyecto: {relative}')
    target = root.joinpath(*name.parts).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError(f'Ruta fuera del proyecto: {relative}')
    return target


def read_manifest(root: Path) -> dict:
    manifest = json.loads((root / 'reproducibility' / 'artifacts.json').read_text(encoding='utf-8'))
    if manifest.get('schema_version') != 1:
        raise ValueError('Versión desconocida del inventario de artefactos')
    return manifest


def restore_entry(root: Path, entry: dict, *, dry_run: bool = False) -> str:
    archive = project_file(root, entry['archive'])
    target = project_file(root, entry['target'])
    if file_sha256(archive) != entry['archive_sha256']:
        raise ValueError(f'Archivo comprimido alterado: {entry["archive"]}')
    if target.exists():
        if file_sha256(target) != entry['sha256']:
            raise ValueError(f'El destino ya existe con otros bytes; se conserva: {entry["target"]}')
        return 'already_present'
    if dry_run:
        return 'would_restore'
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=target.parent, prefix=target.name + '.', suffix='.tmp', delete=False) as output:
            temporary = Path(output.name)
            with gzip.open(archive, 'rb') as incoming:
                shutil.copyfileobj(incoming, output, length=1024 * 1024)
        if temporary.stat().st_size != entry['size_bytes'] or file_sha256(temporary) != entry['sha256']:
            raise ValueError(f'Los bytes restaurados no coinciden: {entry["target"]}')
        if target.exists():
            raise FileExistsError(f'El destino apareció durante la restauración: {target}')
        os.replace(temporary, target)
        return 'restored'
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=PROJECT_ROOT)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    counts: dict[str, int] = {}
    for entry in read_manifest(args.root)['archives']:
        status = restore_entry(args.root, entry, dry_run=args.dry_run)
        counts[status] = counts.get(status, 0) + 1
    print(json.dumps(counts, indent=2))


if __name__ == '__main__':
    main()
