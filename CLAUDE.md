# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Educational Jupyter notebooks for a ProfAI machine-learning course (content in **Italian**). Each numbered top-level folder is a course module covering one algorithm family (Gradient Descent, Naive Bayes, SVM, Neural Networks, Nearest Neighbors, Decision Tree/Random Forest). Per module there is a lesson notebook plus a `*_exercise.ipynb`. There is no application to build or test suite to run — the deliverable is the notebooks themselves.

## Environment

Use the workspace virtualenv for anything that executes notebook code:

```bash
.venv/bin/python3 <script>      # Python 3.12, has scikit-learn, numpy, pandas, matplotlib, seaborn, jupyter, opencv
```

## Critical convention: notebooks load data and helpers from the remote GitHub repo, not local files

Notebooks were authored in Google Colab. They do **not** read the local `datasets/` or `script/` directories. Instead they fetch from the published `main` branch on GitHub:

- Datasets: `BASE_URL = "https://raw.githubusercontent.com/ProfAI/machine-learning-modelli-e-algoritmi/main/datasets/"`, then `pd.read_csv(BASE_URL + "heart.csv")`.
- Viz helper: `!wget https://raw.githubusercontent.com/ProfAI/.../main/script/viz.py` then `from viz import plot_decision_boundary`.

Implication: editing a CSV in local `datasets/` or `script/viz.py` does **not** change notebook behavior until the change is pushed to `main`. The local `datasets/` copies exist for reference/regeneration only. Some notebooks also reference filenames not present locally (e.g. `spam_balanced.csv`, `penguins.csv`) that live only in the remote repo.

`script/olivetti_faces_exporter.py` regenerates `datasets/olivetti_faces.zip` from sklearn's Olivetti faces; `script/viz.py` provides `plot_decision_boundary(model, train_set, test_set, sv=None)`.

## Editing notebooks

Never hand-edit `.ipynb` JSON. Notebooks carry large HTML/plot outputs — do not Read them raw. Use the pedagogical-enrichment tooling in `.agents/notebook-pedagogical-enrichment/` (see its `SKILL.md` for the full workflow):

```bash
# Summarize cells without dumping outputs
python3 .agents/notebook-pedagogical-enrichment/scripts/notebook_helper.py inspect <notebook.ipynb>
python3 .agents/notebook-pedagogical-enrichment/scripts/notebook_helper.py clear-outputs <notebook.ipynb>

# Execute the notebook and dump real metrics (run with .venv python)
.venv/bin/python3 .agents/notebook-pedagogical-enrichment/scripts/notebook_metric_extractor.py <notebook.ipynb>

# Apply markdown/code cell edits from a JSON spec
python3 .agents/notebook-pedagogical-enrichment/scripts/enrich_runner.py -n <notebook.ipynb> -s <spec.json>
```

`enrich_runner` spec entries: `match_type` ∈ `prefix|exact|contains`, `action` ∈ `insert_before|insert_after|replace|append`, `cell_type` ∈ `markdown|code`. Validate after editing: `python3 -c 'import json; json.load(open("notebook.ipynb"))'`.

When adding explanations, report **exact** metrics obtained by actually executing the notebook (via the extractor), keep prose in Italian, and use LaTeX for loss/penalty formulas.
