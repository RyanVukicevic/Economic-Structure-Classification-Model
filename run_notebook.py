"""Execute every notebook cell in a fresh kernel and save outputs plus a run record."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
import sys
import time

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

ROOT = Path(__file__).resolve().parent


def main():
    # Small matrices run faster without large BLAS/OpenMP thread pools.
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
        os.environ[key] = '1'
    os.environ['MPLBACKEND'] = 'module://matplotlib_inline.backend_inline'
    os.environ['IPYTHONDIR'] = str(ROOT / '.ipython')
    output = ROOT / 'outputs'
    output.mkdir(exist_ok=True)
    path = ROOT / 'economic_structure_classification_model.ipynb'
    notebook = nbformat.read(path, as_version=4)
    for cell in notebook.cells:
        if cell.cell_type == 'code':
            cell.outputs = []
            cell.execution_count = None
    manager = KernelManager(kernel_name='python3')
    manager.kernel_spec.argv = [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}']
    started = time.monotonic()
    def progress(cell, cell_index, **kwargs):
        if cell.cell_type == 'code' and cell.source.strip():
            print(f'Cell {cell_index} completed ({time.monotonic() - started:.0f}s)', flush=True)
    client = NotebookClient(notebook, km=manager, timeout=1800,
                            resources={'metadata': {'path': str(ROOT)}},
                            on_cell_executed=progress)
    try:
        client.execute()
    except Exception:
        nbformat.write(notebook, output / 'failed-notebook.ipynb')
        raise
    finally:
        if manager.has_kernel:
            manager.shutdown_kernel(now=True)
    nbformat.validate(notebook)
    nbformat.write(notebook, path)
    records = []
    for i, cell in enumerate(notebook.cells):
        if cell.cell_type == 'code':
            text = ''.join(o.get('text', '') for o in cell.outputs if o.output_type == 'stream')
            if 'Accuracy:' in text or 'Accuracy' in text:
                records.append({'cell': i, 'output': text})
    with (ROOT / 'lr_wiod_wiot_wide.csv').open('rb') as stream:
        checksum = hashlib.file_digest(stream, 'sha256').hexdigest()
    packages = ['numpy', 'pandas', 'scipy', 'scikit-learn', 'matplotlib',
                'seaborn', 'kneed', 'nbformat', 'nbclient', 'ipykernel']
    report = {
        'completed_at_utc': datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds': round(time.monotonic() - started, 2),
        'executed_code_cells': sum(c.cell_type == 'code' and c.execution_count is not None for c in notebook.cells),
        'errors': sum(o.output_type == 'error' for c in notebook.cells if c.cell_type == 'code' for o in c.outputs),
        'csv_sha256': checksum,
        'python': sys.version.split()[0],
        'versions': {p: importlib.metadata.version(p) for p in packages},
        'recorded_metrics': records,
    }
    (output / 'run_summary.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f"SUCCESS: {report['executed_code_cells']} cells, {report['errors']} errors", flush=True)


if __name__ == '__main__':
    main()
