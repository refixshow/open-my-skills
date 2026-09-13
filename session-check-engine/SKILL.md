---
name: session-check-engine
description: Review coaching-session transcripts with a source-grounded High Performance methodology, an optional second sieve of general coaching tools, transcript-backed post-session forms, longitudinal coach-development tracking, and one-prompt-at-a-time practice. Use when Codex receives a coaching transcript or session recording; when the user asks to check, supervise, compare, improve, score, summarize, or practise a coaching session; when they ask whether a High Performance session stayed on topic; or when they need a course term, session framework, tool, progress check, or source-corpus diagnostic. Treat a transcript supplied without instructions as a request for the complete check-session flow. Do not use for diagnosis, psychotherapy, medical or crisis assessment, or judging general coach competence from one transcript.
---

Operate one self-contained, private, source-grounded coaching supervision system. Compare functions, not memorized scripts.

## Setup

Before any command:

1. Run `python -X utf8 <skill-base>/scripts/context.py --root <workspace>` once per session with cwd set to the coaching workspace.
2. Follow the printed bundled-library paths. Never reconstruct the High Performance method from general model knowledge.
3. Load only the command reference selected below, then `references/high-performance/catalog.md` or `references/coaching-tools/catalog.md` and the exact session or tool cards required for the request.
4. Confirm that the analyzed artifact is a client-session transcript rather than an instructor lecture. If only audio is supplied, transcribe locally when the harness supports it; preserve timestamps and uncertain speakers.
5. Keep raw recordings, transcripts, client identifiers, and case narratives out of the skill and durable development state.

## Operating modes

Choose the smallest mode that completes the job.

**Review mode — default.** Analyze the current transcript and return the report in conversation. Do not persist the transcript, quotations, client facts, or report.

**Development mode — enabled only when `.coaching-supervision/coach-development.json` exists with `tracking_enabled: true`, or the user explicitly opts in.** Freeze the current-session verdict first, then compare observable coach behaviors and store only de-identified timestamp anchors, focus areas, and drills.

**Source-maintenance mode — explicit only.** Validate or refresh the local course corpus. Keep raw media and full extracted text in private work directories outside the skill; distill only concise methodology cards with provenance.

## Commands

| Command | Outcome | Required reference |
|---|---|---|
| `doctor` | Read-only readiness, source, privacy, and development-state diagnostic | `references/doctor.md` |
| `check-session [transcript]` | Complete gated review, forms draft, optional progress comparison, and drill queue | `references/check-session.md`, `references/report-contract.md` |
| `hp-review [transcript]` | High Performance method and topic-fidelity review only | `references/check-session.md`, `references/high-performance/catalog.md` |
| `tool-review [transcript]` | General coaching-tool review; provisional when the session is High Performance | `references/check-session.md`, `references/coaching-tools/catalog.md` |
| `forms [transcript]` | Evidence-backed Client Observation plus a blank, coach-owned Self-Evaluation worksheet | `references/forms.md` |
| `progress [transcript]` | Compare frozen current findings with comparable real-session history | `references/progress-practice.md` |
| `practice [focus]` | Start or resume one stored drill, one prompt at a time | `references/progress-practice.md` |
| `knowledge [session/term/tool]` | Explain one source-grounded session, course term, or coaching tool | `references/knowledge-sources.md` |
| `sources [validate/refresh]` | Validate provenance or explicitly refresh source-derived cards | `references/knowledge-sources.md` |

## Routing

- A pasted, attached, linked, or otherwise supplied coaching-session transcript with no instruction routes to `check-session`.
- “Pełny check”, “sprawdź sesję”, “superwizja”, “co poprawić”, “jakich narzędzi zabrakło”, or a later session for comparison routes to `check-session` unless the user explicitly narrows the scope.
- “Tylko High Performance”, topic fidelity, session structure, or drift routes to `hp-review`.
- “Tylko narzędzia”, a non-High-Performance coaching transcript, or one missed-intervention question routes to `tool-review`. For a High Performance session, keep results provisional until the first sieve exists.
- Observation-sheet or self-evaluation paperwork routes to `forms`.
- “Czy jest progres”, “porównaj z poprzednią”, or regression routes to `progress`, but complete and freeze the current review before reading history.
- “Poćwiczmy”, “daj następne ćwiczenie”, or a named focus routes to `practice`.
- A course definition, session framework, or tool explanation routes to `knowledge`.
- With no transcript and no clear command, run `doctor` and recommend 2–3 exact next commands. Do not invent a session to review.
- If two routes remain materially different after inspecting the artifact, ask one precise question. Do not ask the user to choose when the transcript and wording already establish the job.

## Complete review contract

For `check-session`, read [references/check-session.md](references/check-session.md) and follow this order without exception:

1. Preflight transcript reliability and select one declared or defensibly inferred primary High Performance topic.
2. Produce independent `HP_RESULT`, `TOOLS_CANDIDATES`, and `FORMS_DRAFT` payloads. Use parallel agents when the harness supports them; otherwise run the same contracts sequentially and disclose the fallback.
3. Validate the payloads with `scripts/kernel.py validate`.
4. Freeze `HP_RESULT`, then apply `scripts/kernel.py gate`. Admit zero to three tools only after the frozen first sieve.
5. Synthesize one report from [references/report-contract.md](references/report-contract.md). Never paste three agent reports together.
6. Only after sections 1–7 are frozen, enter Development mode when enabled.
7. Bank up to three de-identified drills before presenting the first prompt. If the user asked for analysis only, do not start practice.

## Hard ordering rule

The first sieve asks: **Did this session fulfill its intended High Performance function while preserving coach and client agency?**

The second sieve asks: **Inside that function, could one brief general coaching tool materially deepen the client's work?**

The second answer cannot overrule, soften, or repair the first. A forms draft cannot change either answer.

## Operating laws

1. Treat safety, consent, scope, and transcript uncertainty as higher priority than method fidelity.
2. Review one primary High Performance topic. Load another topic only to test suspected drift.
3. Compare client-facing function, not exact wording or question order.
4. Preserve coach agency inside the method and client agency inside the conversation.
5. Separate transcript observation, functional interpretation, and supervision hypothesis.
6. Use timestamps; when absent, use speaker plus line number or a minimal locating fragment.
7. Infer a topic only with `medium` or `high` confidence. If confidence would be `low`, ask for the intended topic before issuing a High Performance verdict. A partial excerpt without the opening contract that contains signals from two or more pillars is ambiguous by default.
8. Freeze the current first-sieve verdict before tool admission, history, or drills.
9. Admit a tool only when all five gate tests pass: explicit signal, current objective, High Performance dependency satisfied, brief/in-scope use, and added value beyond listening or a simpler move.
10. Zero admitted tools is a valid positive result.
11. Observation-sheet categories are documentation lenses, not a hidden session agenda.
12. For every absent Client Observation field write the literal marker `not discussed in the reviewed transcript`; do not replace it with a looser synonym. Keep every coach-owned Self-Evaluation response and numeric rating blank; never answer private first-person reflection from transcript evidence.
13. Do not infer voice energy, diagnosis, pathology, trauma, hidden motive, or medical meaning from text.
14. Track observable coach behaviors, never fixed traits or general competence.
15. Compare functionally similar opportunities, not raw counts across different topics or transcript lengths.
16. Use `insufficient_evidence` when no comparable opportunity exists; do not translate absence into failure.
17. Simulation is practice evidence only. Confirm transfer from a later real-session transcript.
18. Keep at most three active development focuses and at most three prompts per drill.
19. During practice, present exactly one prompt, wait, give concise feedback, persist advancement, then reveal the next prompt.
20. Stop practice immediately when the user says to stop.
21. Treat local course materials as the instructor's methodology, not independent efficacy evidence.
22. Never send confidential source or session material to an external service without explicit authorization.

## Default locations

- Engine: `<workspace>/.agents/skills/session-check-engine/`
- Bundled High Performance methodology: `<skill-base>/references/high-performance/`
- Bundled general coaching tools: `<skill-base>/references/coaching-tools/`
- De-identified development state: `<workspace>/.coaching-supervision/coach-development.json`
- Private High Performance work corpus: `<workspace>/high-performance-work/`
- Private general-coaching work corpus: `<workspace>/work/`

Create or change durable development state only in Development mode. Never create a transcript archive as a side effect of review.
