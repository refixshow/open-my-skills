# Check one coaching session

Use this workflow for a complete transcript review. Keep all analysis lanes independent until the priority gate.

## 1. Intake

1. Confirm that the input is a client-session transcript, not an instructor lecture or course source.
2. State transcript completeness, speaker reliability, timestamp reliability, and material missing context.
3. Use the declared High Performance topic when present. Otherwise infer one primary topic from the opening contract, repeated purpose, exercised material, and closing integration. Label it `inferred` with confidence.
4. Infer only with `medium` or `high` confidence. If confidence would be `low`, ask one precise question for the intended topic before creating `HP_RESULT`. Treat a partial excerpt without the opening contract that contains signals from two or more pillars as ambiguous by default. Never blend topics or pick the first named pillar merely to avoid asking.
5. Read `high-performance/catalog.md`, exactly one primary card from `high-performance/sessions/`, and `high-performance/report-contract.md`.
6. Do not read the development log or earlier feedback yet.

For a clearly non-High-Performance session, skip the High Performance lane, use `coaching-tools/catalog.md` and only relevant cards from `coaching-tools/topics/`, and label the result a general coaching review. Do not pretend that a High Performance topic applies.

## 2. Independent analysis lanes

When parallel agents are available, give each agent the same raw transcript, topic, one-sentence session purpose, and reliability note. Do not pass expected findings, history, or another lane's output. When parallelism is unavailable, run the same contracts sequentially.

### Lane A — `HP_RESULT`

Evaluate only:

- intended session function and arc;
- coach and client agency;
- topic discipline and time use;
- integration, commitment, consent, and safety;
- 2–4 strengths and 2–5 highest-value findings.

Omit generic coaching tools, forms, progress, and exercises. Write a JSON payload matching `assets/schemas/hp-result-v1.json`, validate it, and preserve the validated payload unchanged until the gate.

### Lane B — `TOOLS_CANDIDATES`

Read `coaching-tools/catalog.md` and only shortlisted cards from `coaching-tools/topics/`. Return zero to five provisional opportunities. For every candidate include:

- locatable transcript moment and explicit client signal;
- tool ID, source basis, confidence, and a concise intervention;
- why listening or a simpler move could be better;
- `hp_dependency`;
- five explicit admission booleans.

Omit the High Performance verdict, final admission, history, and drills. Match `assets/schemas/tools-candidates-v1.json` and validate it.

### Lane C — `FORMS_DRAFT`

Read [forms.md](forms.md). Draft Client Observation fields from explicit transcript evidence and use the exact literal marker `not discussed in the reviewed transcript` when that evidence is absent, including in an otherwise Polish report. Render every Coach Self-Evaluation item as a first-person prompt with a blank coach response; leave all numeric ratings blank. Do not convert transcript observations into answers about how the coach privately felt. Match `assets/schemas/forms-draft-v1.json` and validate it.

## 3. Validate and gate

Save temporary lane payloads outside the skill only when the harness needs files for validation; delete or discard them after synthesis.

Run:

```powershell
python -X utf8 <skill-base>/scripts/kernel.py validate hp <hp-result.json>
python -X utf8 <skill-base>/scripts/kernel.py validate tools <tools-candidates.json>
python -X utf8 <skill-base>/scripts/kernel.py validate forms <forms-draft.json>
python -X utf8 <skill-base>/scripts/kernel.py gate --hp <hp-result.json> --tools <tools-candidates.json>
```

Request one correction from the responsible lane when validation fails. Do not ask another lane to reconstruct it.

The gate records a digest of frozen `HP_RESULT`, admits at most three candidates whose five tests all pass, and explains deterministic rejections. It cannot judge semantic truth; the orchestrator remains responsible for checking each boolean against the transcript and source card.

Reopen `HP_RESULT` only for a material transcript-attribution, completeness, safety, or source error. State the correction and create a new validated payload; never silently soften it because a tool seems attractive.

## 4. Synthesize

Use [report-contract.md](report-contract.md). Write one coherent report in priority order. Deduplicate repeated moments without erasing distinct functions. Check every forms entry against the raw transcript.

For `hp-review`, stop after the validated first sieve and use sections 1–4 of the report contract.

For `tool-review` on a High Performance session, return candidates as provisional unless a valid frozen `HP_RESULT` was supplied. For a non-High-Performance session, follow `coaching-tools/report-contract.md`.

## 5. Development and drills

Only after report sections 1–7 are complete and frozen, read [progress-practice.md](progress-practice.md). If Development mode is enabled, compare current evidence, persist de-identified verdicts, and bank up to three drills.

Start the first prompt only when the user did not request analysis-only output. A full report must remain readable even if no practice follows.
