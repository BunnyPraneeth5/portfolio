"""Shared validation for recorded agent replays.

Used by the ProjectReplay model, the admin JSON upload and the
`import_replay` management command, so every path accepts the same format:

    {
      "title": "SOC Copilot investigates a suspicious IP",
      "duration_s": 42,
      "steps": [
        {"t": 0, "actor": "orchestrator", "kind": "info", "text": "received alert"}
      ]
    }
"""

import ipaddress
import json
import math
import re

KINDS = ('info', 'tool_call', 'result', 'error')
MAX_STEPS = 300
MAX_TEXT = 500
MAX_ACTOR = 40
MAX_TITLE = 200
MAX_DURATION_S = 3600
MAX_FILE_BYTES = 512 * 1024
MAX_ERRORS = 20

# Safety net for the manual sanitization checklist: block obvious leaks.
_EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
_SECRETS = [
    (re.compile(r'\b(?:sk|pk|rk)-[A-Za-z0-9_-]{16,}'), 'an API key (sk-/pk-/rk-...)'),
    (re.compile(r'\bgh[pousr]_[A-Za-z0-9]{20,}'), 'a GitHub token'),
    (re.compile(r'\bAKIA[0-9A-Z]{16}\b'), 'an AWS access key'),
    (re.compile(r'\bxox[abpr]-[A-Za-z0-9-]{10,}'), 'a Slack token'),
    (re.compile(r'\bAIza[0-9A-Za-z_-]{30,}'), 'a Google API key'),
    (re.compile(r'\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+'), 'a JWT'),
    (re.compile(r'(?i)\bbearer\s+[A-Za-z0-9._~+/-]{16,}'), 'a bearer token'),
    (re.compile(r'(?i)\b(?:api[_-]?key|secret|password|passwd|token)\s*[:=]\s*\S+'), 'a key=value secret'),
    (re.compile(r'\b[0-9a-fA-F]{32,}\b'), 'a long hex string (key or hash)'),
]
_IPV4 = re.compile(r'(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])')


class ReplayValidationError(ValueError):
    """Raised with a list of human-readable messages."""

    def __init__(self, messages):
        self.messages = list(messages)
        super().__init__('; '.join(self.messages))


def parse_replay_json(raw):
    """Decode bytes/str into a Python object, with a readable error."""
    if isinstance(raw, bytes):
        if len(raw) > MAX_FILE_BYTES:
            raise ReplayValidationError([f'File is larger than {MAX_FILE_BYTES // 1024} KB.'])
        try:
            raw = raw.decode('utf-8-sig')
        except UnicodeDecodeError:
            raise ReplayValidationError(['File is not UTF-8 text.'])
    try:
        return json.loads(raw)
    except json.JSONDecodeError as err:
        raise ReplayValidationError([f'Not valid JSON: {err.msg} (line {err.lineno}, column {err.colno}).'])


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def find_leaks(text):
    """Return descriptions of obvious sensitive data found in `text`."""
    found = []
    if _EMAIL.search(text):
        found.append('an email address')
    for pattern, label in _SECRETS:
        if pattern.search(text):
            found.append(label)
    for match in _IPV4.finditer(text):
        try:
            ip = ipaddress.IPv4Address(match.group())
        except ipaddress.AddressValueError:
            continue
        # is_private also covers the documentation ranges 192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24.
        if not (ip.is_private or ip.is_loopback or ip.is_unspecified):
            found.append(f'a public IP address ({match.group()}); use a documentation IP like 203.0.113.7')
    return found


def validate_replay(doc):
    """Validate a decoded replay document. Returns a normalized dict or raises ReplayValidationError."""
    errors = []

    def add(message):
        if len(errors) < MAX_ERRORS:
            errors.append(message)

    if not isinstance(doc, dict):
        raise ReplayValidationError(['Top level must be a JSON object with "title", "duration_s" and "steps".'])

    title = doc.get('title')
    if not isinstance(title, str) or not title.strip():
        add('"title" must be a non-empty string.')
    elif len(title) > MAX_TITLE:
        add(f'"title" is longer than {MAX_TITLE} characters.')
    else:
        for leak in find_leaks(title):
            add(f'"title" contains {leak}.')

    duration = doc.get('duration_s')
    if not _is_number(duration) or duration < 0:
        add('"duration_s" must be a number of seconds (0 or more).')
        duration = None
    elif duration > MAX_DURATION_S:
        add(f'"duration_s" is over {MAX_DURATION_S} seconds.')
        duration = None

    steps = doc.get('steps')
    normalized = []
    if not isinstance(steps, list) or not steps:
        add('"steps" must be a non-empty list.')
    elif len(steps) > MAX_STEPS:
        add(f'Too many steps: {len(steps)} (maximum {MAX_STEPS}). Trim the run before importing.')
    else:
        previous_t = 0
        for index, step in enumerate(steps, start=1):
            label = f'Step {index}'
            if not isinstance(step, dict):
                add(f'{label}: must be an object with t, actor, kind, text.')
                continue
            t = step.get('t')
            if not _is_number(t) or t < 0:
                add(f'{label}: "t" must be a number of seconds (0 or more).')
            else:
                if t < previous_t:
                    add(f'{label}: "t" ({t}) is earlier than the previous step ({previous_t}); steps must be in time order.')
                if duration is not None and t > duration:
                    add(f'{label}: "t" ({t}) is after "duration_s" ({duration}).')
                previous_t = max(previous_t, t)
            actor = step.get('actor')
            if not isinstance(actor, str) or not actor.strip():
                add(f'{label}: "actor" must be a non-empty string.')
            elif len(actor) > MAX_ACTOR:
                add(f'{label}: "actor" is longer than {MAX_ACTOR} characters.')
            kind = step.get('kind')
            if kind not in KINDS:
                add(f'{label}: unknown kind {kind!r} (allowed: {", ".join(KINDS)}).')
            text = step.get('text')
            if not isinstance(text, str) or not text.strip():
                add(f'{label}: "text" must be a non-empty string.')
            elif len(text) > MAX_TEXT:
                add(f'{label}: "text" is {len(text)} characters (maximum {MAX_TEXT}); shorten it to a one-line summary.')
            for field_name, value in (('actor', actor), ('text', text)):
                if isinstance(value, str):
                    for leak in find_leaks(value):
                        add(f'{label}: "{field_name}" contains {leak}.')
            if isinstance(t, (int, float)) and isinstance(actor, str) and isinstance(text, str):
                normalized.append({'t': t, 'actor': actor.strip(), 'kind': kind, 'text': text.strip()})

    if errors:
        raise ReplayValidationError(errors)
    return {
        'title': title.strip(),
        # Round up so every step time stays within the stored duration.
        'duration_s': math.ceil(duration),
        'steps': normalized,
    }


def load_replay_file(raw):
    """Parse and validate raw file contents in one go."""
    return validate_replay(parse_replay_json(raw))
