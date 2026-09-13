# Development progress and practice

Enter this layer only after the current-session report is frozen.

## State

Use `.coaching-supervision/coach-development.json`. Create it only after explicit opt-in. Operate it through `scripts/development_log.py`; do not edit it manually.

Allowed comparison verdicts are `baseline`, `progress`, `mixed`, `no_progress`, `regression`, and `insufficient_evidence`.

## Compare progress

1. Read active focuses only after the current review is complete.
2. Locate realistic current opportunities for each replacement behavior.
3. Compare functionally similar moments, not raw counts.
4. Use `progress` when the replacement behavior appears reliably and the old behavior materially decreases.
5. Use `mixed` when both remain visible.
6. Use `no_progress` only when the old behavior repeats across multiple comparable moments without meaningful replacement.
7. Use `regression` only when comparable evidence is materially worse than the established baseline.
8. Use `insufficient_evidence` when opportunity or transcript coverage is inadequate.
9. Move a focus to monitoring only after improvement across at least two real sessions. Close it only when stable and the user agrees.
10. Add a new active focus only when the issue repeats, materially affects the session, or the user explicitly chooses it. Keep at most three active focuses.

Store only the session topic and de-identified timestamp anchors. Never store names, quotations, transcript paths, employer/health details, or case narrative.

## Generate drills

Create at most three drills from the highest-leverage current focuses. Every drill must have a stable ID, source session label, observable trigger, one target behavior, 1–3 complete prompts, a portable rule, and status.

Reuse an equivalent planned drill. Store the complete drill before showing its first prompt.

## Interactive practice

Run:

```powershell
python -X utf8 <skill-base>/scripts/development_log.py --root <workspace> next-exercise
```

Present only the returned current prompt as `Ćwiczenie X / Pytanie N`, then wait. After concise feedback run `advance-exercise` with the returned focus and drill IDs. Do not expose later prompts early.

Correct simulation performance is practice evidence, never proof of transfer. Stop immediately when the user asks to stop.
