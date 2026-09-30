# Notebooks

Empty by design. Exploratory data analysis and data-quality validation for
this project were done directly against the processed DataFrames (see the
"Honest results" and data-quality notes in `docs/IMPLEMENTATION_PLAN.md` for
what was checked and what was found — including two real bugs caught this
way: a pagination bug that silently truncated race results, and a status-
classification bug that inflated the apparent DNF rate).

All reusable logic lives in `backend/ml/` as plain Python modules, not
notebook cells, so it's tested and importable — per the project's own rule
that ML code belongs in modules, with notebooks reserved for genuinely
throwaway exploration. Add one here if you want to poke at the data
interactively; none was needed to build this project.
