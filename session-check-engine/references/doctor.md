# Doctor

Diagnose readiness without changing files.

## Procedure

1. Run `python -X utf8 <skill-base>/scripts/doctor.py --root <workspace> --json`.
2. If `status` is `blocked`, report the exact missing or invalid dependency. Do not improvise proprietary methodology.
3. If `status` is `needs-attention`, distinguish a stale/invalid development log from a source-corpus problem.
4. If `status` is `ready`, report source-card counts, tracking mode, queued drills, and 2–3 exact next commands.
5. Add `--deep` only when source maintenance, recent source edits, or a suspected corpus error makes the slower validators useful.

## Status meaning

- `ready`: both methodology libraries are present and structurally usable.
- `needs-attention`: review can proceed, but development state or a deep source check needs repair.
- `blocked`: a required sibling skill, catalog, session card, or tool card is unavailable.

Doctor is read-only. A recommendation is not authorization to refresh sources, create state, or analyze an absent transcript.
