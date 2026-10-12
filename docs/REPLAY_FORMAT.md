# Replay format

Replays are recorded agent runs played back on the site like a terminal. They are never live.
One JSON file per run:

```json
{
  "title": "SOC Copilot investigates a suspicious IP",
  "duration_s": 42,
  "steps": [
    {"t": 0, "actor": "orchestrator", "kind": "info", "text": "received alert"},
    {"t": 2, "actor": "orchestrator", "kind": "info", "text": "dispatching 4 agents"},
    {"t": 5, "actor": "recon", "kind": "tool_call", "text": "lookup_ip 203.0.113.7"},
    {"t": 9, "actor": "recon", "kind": "result", "text": "finding summary"}
  ]
}
```

The example above is illustrative only. A copy is in `docs/examples/replay-example.json`.

## Rules (checked on every import)

- `title`: non-empty, up to 200 characters.
- `duration_s`: seconds, 0 to 3600.
- `steps`: 1 to 300 steps, in time order. Each step has:
  - `t`: seconds from the start, not after `duration_s`.
  - `actor`: up to 40 characters.
  - `kind`: one of `info`, `tool_call`, `result`, `error`.
  - `text`: up to 500 characters. Shorten long tool output to a one-line summary.
- File size up to 512 KB, UTF-8.

## Sanitization checklist (run before importing)

- No API keys, tokens, file paths, usernames, real IPs, emails or private data.
- Shorten long tool outputs to one-line summaries.

The validator also blocks obvious leaks as a safety net: email addresses, token-looking strings
(`sk-...`, `ghp_...`, `AKIA...`, JWTs, bearer tokens, `key=value` secrets, hex strings of 32+ characters)
and public IPv4 addresses. Use documentation IPs such as `192.0.2.10`, `198.51.100.23` or `203.0.113.7` instead.
This does not replace the manual checklist.

## Adding a replay

**Admin (no terminal):** Project replays, Add. Pick the project, upload the JSON file, save.
Title and duration are filled from the file if left empty. Replays start unpublished: tick
"Is published" after checking. "Is featured on home" makes it play first on the homepage (only one at a time).

**Command line (backup path):**

```bash
python manage.py import_replay soc-copilot path/to/run.json
```

Options: `--title`, `--order`, `--publish`, `--feature-on-home`. Malformed files are rejected with a list of what to fix.

Raw logs never go in the repo.
