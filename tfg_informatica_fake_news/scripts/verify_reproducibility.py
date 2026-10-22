"""Verify the documented artefacts and optionally recalculate saved-prediction metrics.

This command does not train classifiers or modify experimental outputs.
Only Python's standard library is required.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import gzip
import json
import math
from pathlib import Path
import statistics

from scripts.restore_artifacts import PROJECT_ROOT, file_sha256, project_file, read_manifest


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def verify_inventory(root: Path, inventory: dict) -> dict:
    for item in inventory['files']:
        path = project_file(root, item['path'])
        require(path.is_file(), f'Falta {item["path"]}')
        require(path.stat().st_size == item['size_bytes'] and file_sha256(path) == item['sha256'],
                f'Contenido alterado: {item["path"]}')
    for item in inventory['archives']:
        for field, hash_key in [('archive', 'archive_sha256'), ('target', 'sha256')]:
            path = project_file(root, item[field])
            require(path.is_file(), f'Falta {item[field]}; ejecute python -m scripts.restore_artifacts')
            require(file_sha256(path) == item[hash_key], f'Contenido alterado: {item[field]}')
    return {'direct_files': len(inventory['files']), 'restored_archives': len(inventory['archives'])}


def read_rows(path: Path) -> list[dict]:
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def confusion(rows: list[dict]) -> list[list[int]]:
    matrix = [[0, 0], [0, 0]]
    for row in rows:
        truth, prediction = int(row['label']), int(row['pred'])
        require(truth in (0, 1) and prediction in (0, 1), 'Etiqueta binaria inválida')
        matrix[truth][prediction] += 1
    return matrix


def metrics(rows: list[dict]) -> dict:
    matrix = confusion(rows)
    divide = lambda a, b: a / b if b else 0.0
    precision, recall, f1 = [], [], []
    for label in (0, 1):
        correct = matrix[label][label]
        predicted = sum(matrix[row][label] for row in (0, 1))
        actual = sum(matrix[label])
        precision.append(divide(correct, predicted))
        recall.append(divide(correct, actual))
        f1.append(divide(2 * correct, predicted + actual))
    return {'accuracy': divide(matrix[0][0] + matrix[1][1], len(rows)),
            'precision_macro': statistics.mean(precision), 'recall_macro': statistics.mean(recall),
            'macro_f1': statistics.mean(f1)}


def compare(actual: dict, expected: dict, label: str) -> None:
    for key, value in expected.items():
        require(math.isclose(actual[key], value, rel_tol=1e-12, abs_tol=1e-12), f'Métrica diferente en {label}: {key}')


def verify_results(root: Path, run_id: str) -> dict:
    run_dir = root / 'reports' / 'robustness_runs' / run_id
    manifest = json.loads((run_dir / 'robustness_manifest.json').read_text(encoding='utf-8'))
    require(manifest['status'] == 'completed', 'La ejecución principal no está completa')
    assignments = read_rows(run_dir / 'fold_assignments.csv')
    assigned = {row['source_id']: row for row in assignments}
    require(len(assigned) == len(assignments) == manifest['preparation']['derived_rows'], 'Cobertura de particiones incorrecta')
    group_folds = defaultdict(set)
    group_sources = defaultdict(set)
    for row in assignments:
        group_folds[row['duplicate_group']].add(row['fold'])
        group_sources[row['duplicate_group']].add(row['dataset_name'])
    require(all(len(folds) == 1 for folds in group_folds.values()), 'Un grupo está repartido entre folds')
    require({row['fold'] for row in assignments} == {'1', '2', '3', '4', '5'}, 'No hay cinco particiones')
    sources = {row['dataset_name'] for row in assignments}
    require(sources == {'archive2_news_dataset', 'liar_politifact'}, 'Fuente ajena al experimento')
    for name, result in manifest['cross_validation']['models'].items():
        rows = read_rows(run_dir / f'{name}_oof_predictions.csv')
        require(len(rows) == len(assigned) and {row['source_id'] for row in rows} == set(assigned), f'Cobertura OOF incorrecta: {name}')
        for row in rows:
            original = assigned[row['source_id']]
            require(all(row[field] == original[field] for field in ('label', 'dataset_name', 'duplicate_group', 'fold')), f'Asignación OOF diferente: {name}')
        compare(metrics(rows), result['global'], name)
        require(confusion(rows) == result['confusion_matrix'], f'Matriz diferente: {name}')
        per_source = defaultdict(list)
        for row in rows:
            per_source[row['dataset_name']].append(row)
        for source, subset in per_source.items():
            compare(metrics(subset), result['by_source'][source]['metrics'], source)
            require(confusion(subset) == result['by_source'][source]['confusion_matrix'], f'Matriz diferente: {source}')
        fold_results = []
        for fold in range(1, 6):
            subset = read_rows(run_dir / f'{name}_fold_{fold}_predictions.csv')
            expected_ids = {key for key, item in assigned.items() if item['fold'] == str(fold)}
            require(len(subset) == len(expected_ids) and {row['source_id'] for row in subset} == expected_ids, f'Fold incompleto: {name}:{fold}')
            require(all(row['fold'] == str(fold) for row in subset), 'Fold incorrecto en predicciones')
            calculated = metrics(subset)
            compare(calculated, result['folds'][fold - 1]['metrics'], f'{name}:{fold}')
            fold_results.append(calculated)
        compare({key: statistics.mean(row[key] for row in fold_results) for key in fold_results[0]}, result['mean'], name + ':media')
        compare({key: statistics.stdev(row[key] for row in fold_results) for key in fold_results[0]}, result['sample_std'], name + ':desviación')
    for direction, candidates in manifest['transfer'].items():
        for name, result in candidates.items():
            rows = read_rows(run_dir / f'transfer_{direction}_{name}_predictions.csv')
            expected = {key for key, item in assigned.items() if item['dataset_name'] == result['test_source'] and len(group_sources[item['duplicate_group']]) == 1}
            require(len(rows) == len(expected) == result['test_rows'] and {row['source_id'] for row in rows} == expected, f'Transferencia incompleta: {direction}:{name}')
            compare(metrics(rows), result['metrics'], direction + ':' + name)
            require(confusion(rows) == result['confusion_matrix'], f'Matriz de transferencia diferente: {direction}:{name}')
    audit = read_rows(root / 'data' / 'derived' / 'robustness' / run_id / 'exclusion_audit.csv')
    states = Counter(row['status'] for row in audit)
    require(len(audit) == manifest['preparation']['source_rows'], 'Auditoría incompleta')
    require(states == {'retained_representative': 44408, 'deduplicated_exact': 6090, 'excluded_conflicting_duplicate_group': 5}, f'Conciliación diferente: {states}')
    return {'run_id': run_id, 'derived_rows': len(assigned), 'audit_rows': len(audit),
            'models': 2, 'grouped_fits': 10, 'transfer_fits': 4, 'group_leakage': False,
            'audit_states': dict(states), 'saved_metrics_match': True}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=PROJECT_ROOT)
    parser.add_argument('--check-results', action='store_true')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    inventory = read_manifest(args.root)
    output = {'inventory': verify_inventory(args.root, inventory)}
    if args.check_results:
        output['results'] = verify_results(args.root, inventory['primary_run'])
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
