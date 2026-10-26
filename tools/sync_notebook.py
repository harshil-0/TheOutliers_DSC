"""Synchronize the visible notebook cells with analysis.py; optionally execute.

Usage: python tools/sync_notebook.py --execute
Requires nbformat, nbclient and ipykernel for execution. Core analysis requirements
are checked and, if needed, installed by the notebook's first code cell.
"""
from pathlib import Path
import argparse
import json
import re
import sys

import nbformat

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--execute', action='store_true')
args = parser.parse_args()

intro = """# The Outliers: first-basket variety and 90-day customer behaviour

CSE558 Data Science, IIIT-Delhi, Monsoon 2026. Five main hypothesis tests.

**Team:** Aayush Gupta (2023014), Harshil (2023235), Raghav Mittal (2023415),
Utkarsh (2023569), Jaideep Dahiya (2023254).

**Repository:** https://github.com/harshil-0/TheOutliers_DSC

**Run:** execute all cells in order. In this repository, the bundled original
workbook is used. In a fresh Colab runtime, the first analysis cell downloads the
original UCI workbook and creates `retail_project/`. All analysis is visible below;
the notebook does not execute an unseen remote Python script.

**AI assistance:** Generative AI assisted code, statistical analysis and report
drafting. The report lists assigned team responsibilities without claiming
independent, unaided authorship.

**Source:** Chen, D. (2015), Online Retail, UCI, https://doi.org/10.24432/C5BW33,
CC BY 4.0. Outputs measure eligible gross merchandise purchases, not net revenue.
"""
installer = """import importlib.metadata, subprocess, sys
packages = {
    'numpy': ('1.26', 'numpy>=1.26'),
    'pandas': ('2.0', 'pandas>=2.0'),
    'scipy': ('1.11', 'scipy>=1.11'),
    'matplotlib': ('3.7', 'matplotlib>=3.7'),
    'openpyxl': ('3.1', 'openpyxl>=3.1'),
}
needed = []
for package, (minimum, spec) in packages.items():
    try:
        installed = tuple(int(x) for x in importlib.metadata.version(package).split('.')[:2])
        required = tuple(int(x) for x in minimum.split('.')[:2])
        if installed < required:
            needed.append(spec)
    except importlib.metadata.PackageNotFoundError:
        needed.append(spec)
if needed:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', *needed])
print('Core dependency version checks passed.')
"""
cells = [nbformat.v4.new_markdown_cell(intro),
         nbformat.v4.new_markdown_cell((ROOT/'ANALYSIS_PLAN.md').read_text()),
         nbformat.v4.new_markdown_cell('## Dependencies\nCheck installed versions as well as package presence.'),
         nbformat.v4.new_code_cell(installer)]
source = (ROOT/'analysis.py').read_text(encoding='utf-8')
sections = re.split(r'^# %% (.+)\n', source, flags=re.MULTILINE)
for i in range(1, len(sections), 2):
    title, code = sections[i], sections[i+1]
    cells.extend([nbformat.v4.new_markdown_cell('## '+title), nbformat.v4.new_code_cell(code.strip())])
cells.append(nbformat.v4.new_code_cell("""# Display the six generated figures inline.
from IPython.display import display, Image
for image_path in sorted((ROOT / 'figures').glob('*.png')):
    display(Image(filename=str(image_path)))
"""))
cells.append(nbformat.v4.new_markdown_cell("""## Interpretation

T1-T3 retain their original effects and remain significant after Holm adjustment
across all five tests. The unadjusted return-probability gap is +10.85 percentage
points; adjustment for initial spending, units and month leaves its incremental
association uncertain. Higher mean log(1+spend) does not establish higher
arithmetic revenue. Returning customers have about 6.09 fewer SKUs on the second
shopping day.

T4 estimates a broad-minus-narrow return gap of +0.770 days (95% CI -3.076 to
4.617); T5 estimates Spearman rho=0.0236 (bootstrap CI -0.0413 to 0.0890).
Neither added test rejects its null after the five-test Holm adjustment. These
are conditional findings among observed returners, not proof of equality or
causal effects. The plan records the staged addition of T4/T5 before their tests.

The report uses the professor's supplied LaTeX template. Its numerical macros
are regenerated from the same analysis. Compile `report.tex` to update the PDF;
executing this notebook regenerates data, results and figures, but does not
compile LaTeX or publish anything to GitHub.
"""))
notebook = nbformat.v4.new_notebook(cells=cells)
notebook.metadata['kernelspec']={'display_name':'Python 3','language':'python','name':'python3'}
notebook.metadata['language_info']={'name':'python','version':sys.version.split()[0]}
if args.execute:
    from nbclient import NotebookClient
    from jupyter_client import KernelManager
    # Use this interpreter, avoiding accidental selection of another Python installation.
    manager = KernelManager(kernel_name='python3')
    manager.kernel_spec.argv = [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}']
    def report_cell(cell, cell_index, **kwargs):
        print(f'Executing notebook cell {cell_index + 1}: {cell.source.splitlines()[0][:80]}',flush=True)
    client = NotebookClient(notebook, km=manager, timeout=600, startup_timeout=60,
                            resources={'metadata':{'path':str(ROOT)}}, allow_errors=False,
                            on_cell_execute=report_cell)
    client.execute()
    streams = [''.join(o.get('text','')) for cell in notebook.cells for o in cell.get('outputs',[])
               if o.output_type=='stream' and o.get('name')=='stdout']
    (ROOT/'results/run_log.txt').write_text('\n'.join(streams),encoding='utf-8')
    print('Notebook executed successfully with',sum(c.cell_type=='code' for c in notebook.cells),'code cells.')
nbformat.write(notebook, ROOT/'project.ipynb')
print('Saved',ROOT/'project.ipynb')
