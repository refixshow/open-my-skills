# Knowledge and sources

## Knowledge lookup

Route to exactly one local library:

- High Performance session structure or term: read `high-performance/catalog.md`, then one card from `high-performance/sessions/` or `high-performance/definitions.md`.
- General coaching tool: read `coaching-tools/catalog.md`, then one card from `coaching-tools/topics/`.

State that the answer represents the instructor's local methodology. Cite source IDs plus recorded PDF pages or audio timestamps. If sources conflict, report the discrepancy instead of silently normalizing it.

Do not load all cards for one definition. Do not treat a lecture transcript as a client session.

## Validate sources

Run the bundled-library validator:

```powershell
python -X utf8 <skill-base>/scripts/validate_knowledge.py
```

Use `doctor --deep` to orchestrate both checks.

## Refresh sources

Refresh only after explicit authorization and only when the authorized private corpus is available outside the skill. Preserve independent PDF-page and audio-timestamp provenance. Keep full recordings, PDFs, extracted text, and transcripts outside the skill. Distill concise original cards into the two bundled libraries; never bundle long proprietary quotations.
