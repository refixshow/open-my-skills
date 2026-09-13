# Open My Skills

Public Codex skills from refixshow.

## session-check-engine

Reviews coaching-session transcripts using the bundled High Performance and coaching methodology, prepares session feedback and forms, tracks coach development, and supports focused practice.

### Install in the current project

Open the target folder in Codex and install only this skill:

```sh
npx --yes skills@latest add refixshow/open-my-skills --skill session-check-engine --agent codex --copy
```

When prompted, choose the project/local installation. The expected destination is:

```text
.agents/skills/session-check-engine/
```

If Node.js, `npx`, or Git is unavailable, ask Codex to use its built-in `skill-installer` download method and set the destination to the current workspace's `.agents/skills` directory. The source URL is:

```text
https://github.com/refixshow/open-my-skills/tree/main/session-check-engine
```

After installation, start a new Codex turn so the skill can be discovered.
