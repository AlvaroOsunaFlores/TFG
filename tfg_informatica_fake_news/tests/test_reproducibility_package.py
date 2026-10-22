from __future__ import annotations

import gzip
from pathlib import Path

import pytest
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from scripts.restore_artifacts import file_sha256, project_file, restore_entry
from scripts.verify_reproducibility import metrics


def archive_entry(root: Path) -> dict:
    archive = root / 'model.gz'
    content = b'preserved experimental bytes\r\n'
    archive.write_bytes(gzip.compress(content, mtime=0))
    reference = root / 'reference.bin'
    reference.write_bytes(content)
    return {'archive': 'model.gz', 'target': 'models/restored.bin',
            'archive_sha256': file_sha256(archive), 'sha256': file_sha256(reference),
            'size_bytes': len(content)}


def test_restore_preserves_original_bytes_and_is_idempotent(tmp_path: Path) -> None:
    entry = archive_entry(tmp_path)
    assert restore_entry(tmp_path, entry, dry_run=True) == 'would_restore'
    assert not (tmp_path / entry['target']).exists()
    assert restore_entry(tmp_path, entry) == 'restored'
    assert file_sha256(tmp_path / entry['target']) == entry['sha256']
    assert restore_entry(tmp_path, entry) == 'already_present'


def test_restore_refuses_to_replace_different_existing_file(tmp_path: Path) -> None:
    entry = archive_entry(tmp_path)
    target = tmp_path / entry['target']
    target.parent.mkdir()
    target.write_bytes(b'user changes')
    with pytest.raises(ValueError, match='se conserva'):
        restore_entry(tmp_path, entry)
    assert target.read_bytes() == b'user changes'


def test_restore_rejects_corrupted_archive_before_creating_target(tmp_path: Path) -> None:
    entry = archive_entry(tmp_path)
    (tmp_path / entry['archive']).write_bytes(b'corrupted')
    with pytest.raises(ValueError, match='alterado'):
        restore_entry(tmp_path, entry)
    assert not (tmp_path / entry['target']).exists()


def test_restore_rejects_path_outside_project(tmp_path: Path) -> None:
    for name in ('../outside', '/outside', 'C:/outside', 'models\\outside'):
        with pytest.raises(ValueError, match='fuera del proyecto'):
            project_file(tmp_path, name)


def test_saved_prediction_metrics_agree_with_sklearn() -> None:
    truth, prediction = [0, 0, 0, 1, 1, 1, 1], [0, 1, 0, 1, 0, 1, 1]
    rows = [{'label': str(a), 'pred': str(b)} for a, b in zip(truth, prediction)]
    result = metrics(rows)
    assert result['accuracy'] == pytest.approx(accuracy_score(truth, prediction))
    assert result['macro_f1'] == pytest.approx(f1_score(truth, prediction, average='macro'))
    assert result['precision_macro'] == pytest.approx(precision_score(truth, prediction, average='macro'))
    assert result['recall_macro'] == pytest.approx(recall_score(truth, prediction, average='macro'))
