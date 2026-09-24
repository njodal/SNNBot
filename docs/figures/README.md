# Figures

The scripts that draw the figures of the specs. Each one writes a single
`.png` into [`../images/`](../images), and is run from the root of the
repository:

```
python3 docs/figures/tape_retina.py
```

They need `matplotlib`, which the core of the project does not — see
[`requirements.txt`](../../requirements.txt). Nothing here is imported by
`snnbot`, and nothing in `snnbot` imports any of it: these draw what a spec
says, they do not run anything.

| figure | spec |
|--------|------|
| [`tape_retina.py`](tape_retina.py) → `images/tape_retina.png` | [013 — A neuromorphic memory](../../spec/013-neuromorphic-memory.md) |
| [`tiles_retina.py`](tiles_retina.py) → `images/tiles_retina.png` | [014 — A neuromorphic episodic memory](../../spec/014-neuromorphic-episodic-memory.md) |
| [`episodic_sequence_cell.py`](episodic_sequence_cell.py) → `images/episodic_sequence_cell.png` | [014 — A neuromorphic episodic memory](../../spec/014-neuromorphic-episodic-memory.md) |
| [`sequence_cell.py`](sequence_cell.py) → `images/sequence_cell.png` | [010 — Cells](../../spec/010-cells.md) |

The older images were drawn by hand and have no script here.
