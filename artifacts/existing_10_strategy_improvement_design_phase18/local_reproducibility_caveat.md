# Local Reproducibility Caveat

Codex warned that Phase17 depended on local-only Phase16 `runs/` CSVs. Phase18 uses the committed Phase17 curated summaries, but inherits that provenance caveat.

GitHub committed summaries are curated review artifacts, not the full local run tree.

Future reproducibility options:

- keep a local retention policy for Phase16 `runs/`
- add checksums or manifests for local sweep files
- create smaller committed reproducibility summaries
- rerun grids if exact regeneration is needed

Do not stage local `runs/` artifacts in Phase18.
