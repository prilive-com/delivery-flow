"""Read native usage records without changing the logs or the delivery flow.

Only observed Claude transcript and Codex incremental-rollout shapes are counted.
Cumulative Codex counters check completeness; they are never billed as calls.
"""
import argparse
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import stat
import sys
import tomllib

DEFAULT_RECORD_BYTES = 16777216
DEFAULT_CALLS = 100000
METADATA_CHARS = 512
C_FIELDS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")
X_FIELDS = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens", "output_tokens")
X_OPTIONAL = ("reasoning_output_tokens", "total_tokens")
METRICS = ("fresh_input", "cache_write_input", "cache_read_input", "output", "thinking", "raw")
ESSENTIAL = tuple(k for k in METRICS if k != "thinking")
ATTRIBUTION = ("project", "actor", "session", "slice", "stage")
NON_CALLS = {
    "user", "attachment", "system", "cost-state", "result", "rate_limit_event",
    "api-request", "api-request/shape", "api-request/blob", "api-request/shape/blob",
    "permission", "permission-mode", "history", "queue-operation", "file-history-snapshot",
    "progress", "summary", "atis-latch", "last-prompt", "event_msg", "response_item",
    "world_state", "compacted",
}


class Refusal(Exception):
    """Only fixed reason/field names and source locations cross the error boundary."""
    def __init__(self, code, reason, path=None, line=None, field=None):
        super().__init__(reason)
        self.code, self.reason = code, reason
        self.path, self.line, self.field = path, line, field


def _fail(code, reason, path=None, line=None, field=None):
    raise Refusal(code, reason, path, line, field)


def _stamp(value, code=5):
    try:
        if not isinstance(value, str):
            raise ValueError
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.utcoffset() is None:
            raise ValueError
        return dt.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        _fail(code, "BAD_TIMESTAMP" if code == 5 else "INVALID_WINDOW")


def _text(value, required=False):
    if value is None and not required:
        return None
    if not isinstance(value, str) or not value.strip():
        _fail(5, "BAD_METADATA")
    if len(value) > METADATA_CHARS:
        _fail(3, "METADATA_VALUE_LIMIT")
    return value


def _counter(value):
    if value is not None and (type(value) is not int or value < 0):
        _fail(5, "BAD_COUNTER")
    return value


def _digest(parts):
    body = json.dumps(parts, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def _identity(st):
    return st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns


@contextmanager
def _regular(path):
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
    stream = None
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            _fail(3, "NOT_REGULAR", path)
        stream = os.fdopen(fd, "rb")
        fd = None
        yield stream, before
        try:
            stable = (_identity(os.fstat(stream.fileno())) == _identity(before)
                      and _identity(os.stat(path)) == _identity(before))
        except OSError:
            stable = False
        if not stable:
            _fail(3, "SOURCE_CHANGED", path)
    finally:
        if stream is not None:
            stream.close()
        elif fd is not None:
            os.close(fd)


def _pairs(pairs):
    result = {}
    for k, v in pairs:
        if k in result:
            raise ValueError("DUPLICATE_KEY")
        result[k] = v
    return result


def _finite(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("NONFINITE")
    return number


def _constant(value):
    raise ValueError("NONFINITE")


def _records(stream, size, limit, info):
    remaining, number = size, 0
    digest = hashlib.sha256()
    while remaining:
        data = stream.readline(min(limit + 1, remaining + 1))
        number += 1
        if not data:
            _fail(3, "SOURCE_CHANGED", info["path"], number)
        if len(data) > limit:
            _fail(3, "RECORD_LIMIT", info["path"], number)
        remaining -= len(data)
        if remaining < 0:
            _fail(3, "SOURCE_CHANGED", info["path"], number)
        if not data.endswith(b"\n"):
            _fail(5, "TORN_LINE", info["path"], number)
        digest.update(data)
        try:
            row = json.loads(data.decode("utf-8"), object_pairs_hook=_pairs,
                             parse_float=_finite, parse_constant=_constant)
        except (ValueError, UnicodeError, RecursionError):
            _fail(5, "BAD_JSON", info["path"], number)
        if not isinstance(row, dict):
            _fail(5, "BAD_RECORD", info["path"], number)
        yield number, row
    info["sha256"] = digest.hexdigest()


def _manifest(path, limit):
    with _regular(path) as (stream, before):
        if before.st_size > limit:
            _fail(3, "RECORD_LIMIT", path)
        data = stream.read(before.st_size + 1)
    try:
        manifest = tomllib.loads(data.decode("utf-8"))
    except (ValueError, UnicodeError, RecursionError) as exc:
        _fail(2, "TOML_SYNTAX", path, getattr(exc, "lineno", None), "manifest")
    if set(manifest) != {"schema", "source"} or manifest.get("schema") != "dflow.telemetry-input/1":
        _fail(2, "MANIFEST_SCHEMA", path, field="schema/source")
    sources = manifest["source"]
    if not isinstance(sources, list) or not sources:
        _fail(2, "MANIFEST_SOURCE", path, field="source")
    expected = {"format", "path", *ATTRIBUTION}
    resolved = set()
    for i, source in enumerate(sources):
        if not isinstance(source, dict) or set(source) != expected:
            _fail(2, "MANIFEST_KEYS", path, field=f"source[{i}]")
        for k, v in source.items():
            if not isinstance(v, str) or not v.strip() or "\x00" in v:
                _fail(2, "MANIFEST_FIELD", path, field=f"source[{i}].{k}")
            if k != "path" and len(v) > METADATA_CHARS:
                _fail(3, "METADATA_VALUE_LIMIT", path, field=f"source[{i}].{k}")
        if source["format"] not in {"claude", "codex"} or source["actor"] not in {"main", "reviewer", "other"}:
            _fail(2, "MANIFEST_FIELD", path, field=f"source[{i}].format/actor")
        p = Path(source["path"])
        if not p.is_absolute():
            p = path.parent / p
        source["path"] = str(p.absolute())
        canonical = os.path.realpath(p)
        if canonical in resolved:
            _fail(3, "SOURCE_ALIAS", source["path"])
        resolved.add(canonical)
    return sources


def _accounting_shape(row):
    pending = [row]
    keys = {"usage", "token_usage", "total_token_usage", "last_token_usage",
            "thread_token_usage", "turn_token_usage"}
    while pending:
        value = pending.pop()
        if isinstance(value, dict):
            if keys.intersection(value) or any(k.endswith("_tokens") for k in value):
                return True
            pending.extend(value.values())
        elif isinstance(value, list):
            pending.extend(value)
    return False


def _validate_token_fields(usage, fmt):
    """Validate nested counter locations; _usage checks direct counters."""
    ephemeral = ("ephemeral_1h_input_tokens", "ephemeral_5m_input_tokens")
    paths = {}
    if fmt == "claude":
        paths = {("output_tokens_details",): ("thinking_tokens",),
                 ("cache_creation",): ephemeral,
                 ("iterations", "[]"): C_FIELDS,
                 ("iterations", "[]", "cache_creation"): ephemeral}
    pending = [(usage, ())]
    while pending:
        value, path = pending.pop()
        if isinstance(value, dict):
            for key, item in value.items():
                if path and key.endswith("_tokens"):
                    if key not in paths.get(path, ()):
                        _fail(3, "UNKNOWN_ACCOUNTING")
                    if key in ephemeral:
                        _counter(item)
                pending.append((item, path + (key,)))
        elif isinstance(value, list):
            pending.extend((item, path + ("[]",)) for item in value)


def _usage(usage, fmt):
    if not isinstance(usage, dict):
        _fail(5, "BAD_USAGE")
    fields = C_FIELDS if fmt == "claude" else X_FIELDS + X_OPTIONAL
    for key in usage:
        if key.endswith("_tokens") and key not in fields:
            _fail(3, "UNKNOWN_ACCOUNTING")
    _validate_token_fields(usage, fmt)
    values = {k: _counter(usage.get(k)) for k in fields}
    positive_iteration = False
    if fmt == "claude":
        details = usage.get("output_tokens_details")
        if details is None:
            details = {}
        if not isinstance(details, dict):
            _fail(5, "BAD_USAGE")
        values["thinking_tokens"] = _counter(details.get("thinking_tokens"))
        iterations = usage.get("iterations")
        if iterations is None:
            iterations = []
        if not isinstance(iterations, list):
            _fail(3, "UNKNOWN_ACCOUNTING")
        for item in iterations:
            if not isinstance(item, dict):
                _fail(3, "UNKNOWN_ACCOUNTING")
            iteration_values = [_counter(item.get(k)) for k in C_FIELDS]
            positive_iteration |= any((v or 0) > 0 for v in iteration_values)
    return values, positive_iteration


def _invariants(values, fmt, path=None, line=None):
    output = values.get("output_tokens")
    thinking = values.get("thinking_tokens" if fmt == "claude" else "reasoning_output_tokens")
    if output is not None and thinking is not None and thinking > output:
        _fail(5, "BAD_SUBSET", path, line)
    if fmt == "codex":
        inputs, cached = values.get("input_tokens"), values.get("cached_input_tokens")
        if inputs is not None and cached is not None and cached > inputs:
            _fail(5, "BAD_SUBSET", path, line)
        total = values.get("total_tokens")
        if (values.get("cache_write_input_tokens") == 0 and inputs is not None
                and output is not None and total is not None and total != inputs + output):
            _fail(5, "BAD_TOTAL", path, line)


def _metrics(values, fmt):
    inputs, output = values["input_tokens"], values["output_tokens"]
    if fmt == "claude":
        read, write = values["cache_read_input_tokens"], values["cache_creation_input_tokens"]
        fresh, thinking = inputs, values["thinking_tokens"]
        parts = (inputs, read, write, output)
        raw = sum(parts) if all(v is not None for v in parts) else None
    else:
        read, write = values["cached_input_tokens"], values["cache_write_input_tokens"]
        fresh = inputs - read if inputs is not None and read is not None else None
        thinking = values["reasoning_output_tokens"]
        raw = inputs + output if inputs is not None and output is not None and write == 0 else None
    return dict(fresh_input=fresh, cache_write_input=write, cache_read_input=read,
                output=output, thinking=thinking, raw=raw)


@dataclass
class Call:
    ident: str
    collision: str
    native: str
    at: datetime
    values: dict
    execution: dict
    evidence: dict
    positive_iteration: bool = False


def _merge(old, new, fmt):
    if old.native != new.native:
        _fail(5, "CALL_CONFLICT")
    for key, value in new.execution.items():
        previous = old.execution.get(key)
        if previous is not None and value is not None and previous != value:
            _fail(5, "CALL_CONFLICT")
        if previous is None and fmt == "claude":
            old.execution[key] = value
    if fmt == "codex" and old.values != new.values:
        _fail(5, "CALL_CONFLICT")
    if fmt == "claude":
        for key, value in new.values.items():
            if value is not None:
                old.values[key] = max(old.values[key], value) if old.values[key] is not None else value
    old.at = min(old.at, new.at)
    old.evidence["last_line"] = new.evidence["last_line"]
    old.evidence["record_count"] += 1
    old.positive_iteration |= new.positive_iteration


def _reconcile(calls, final, info):
    missing = []
    if final is None:
        missing = list(X_FIELDS)
    else:
        _invariants(final, "codex", info["path"], info.get("counter_line"))
        for field in X_FIELDS + X_OPTIONAL:
            values = [c.values[field] for c in calls]
            if final[field] is None or any(v is None for v in values):
                if field in X_FIELDS:
                    missing.append(field)
                continue
            if sum(values) != final[field]:
                _fail(5, "COUNTER_MISMATCH", info["path"], info.get("counter_line"), field=field)
    info["reconciliation"] = "UNAVAILABLE" if missing else "MATCH"
    info["missing_counter_fields"] = missing
    if missing:
        info.update(state="UNAVAILABLE", reason="COUNTER_UNAVAILABLE")


def _read_source(source, index, limits, identities, inodes):
    fmt, path = source["format"], source["path"]
    info = dict(path=path, format=fmt, session=source["session"], sha256=None, size=None,
                seen_calls=0, selected_calls=0, replayed_ancestor_records=0,
                ignored_records=0, unknown_nonaccounting_records=0, counter_line=None,
                reconciliation="NOT_APPLICABLE", state="AVAILABLE", reason="MEASURED")
    calls, contexts, metas = {}, {}, {}
    primary, final, claude_parent = None, None, None
    line = None
    try:
        with _regular(path) as (stream, before):
            inode = before.st_dev, before.st_ino
            if inode in inodes:
                _fail(3, "SOURCE_ALIAS", path)
            inodes.add(inode)
            info["size"] = before.st_size
            for line, row in _records(stream, before.st_size, limits["max_record_bytes"], info):
                kind = row.get("type")
                if kind is not None and not isinstance(kind, str):
                    _fail(5, "BAD_RECORD")
                if fmt == "codex" and kind in {"session_meta", "turn_context"}:
                    p = row.get("payload")
                    if not isinstance(p, dict):
                        _fail(5, "BAD_METADATA")
                    if kind == "session_meta":
                        if p.get("id") is None:
                            _fail(3, "MISSING_IDENTITY")
                        sid = _text(p.get("id"), True)
                        if p.get("session_id") is not None and p["session_id"] != sid:
                            _fail(5, "SESSION_CONFLICT")
                        record = (_text(p.get("forked_from_id")), _text(p.get("cli_version")))
                        if primary is None:
                            primary = sid
                            if primary != source["session"]:
                                _fail(3, "SESSION_MISMATCH")
                        if sid in metas and metas[sid] != record:
                            _fail(5, "SESSION_CONFLICT")
                        metas[sid] = record
                        if len(metas) > limits["max_calls"]:
                            _fail(3, "METADATA_LIMIT")
                    else:
                        turn = _text(p.get("turn_id"), True)
                        contexts[turn] = dict(model=_text(p.get("model")), effort=_text(p.get("effort")))
                        if len(contexts) > limits["max_calls"]:
                            _fail(3, "CONTEXT_LIMIT")
                    continue
                expected = "assistant" if fmt == "claude" else "token_usage_record"
                if kind != expected:
                    if kind not in NON_CALLS:
                        if _accounting_shape(row):
                            _fail(3, "UNKNOWN_ACCOUNTING")
                        info["unknown_nonaccounting_records"] += 1
                    info["ignored_records"] += 1
                    continue
                if fmt == "claude":
                    p = row.get("message")
                    if not isinstance(p, dict):
                        _fail(5, "BAD_RECORD")
                    values, positive = _usage(p.get("usage", {}), fmt)
                    if p.get("model") == "<synthetic>":
                        if any((v or 0) > 0 for v in values.values()) or positive:
                            _fail(3, "SYNTHETIC_USAGE")
                        info["ignored_records"] += 1
                        continue
                    parent = row.get("sessionId")
                    if parent is None:
                        parent = row.get("session_id")
                    if row.get("sessionId") is not None and row.get("session_id") is not None and row["sessionId"] != row["session_id"]:
                        _fail(5, "SESSION_CONFLICT")
                    sidechain = row.get("isSidechain")
                    if sidechain is not None and type(sidechain) is not bool:
                        _fail(5, "BAD_METADATA")
                    if sidechain is True:
                        native = row.get("agentId")
                    elif sidechain in (None, False) and row.get("agentId") is None:
                        native = parent
                    else:
                        _fail(3, "UNKNOWN_IDENTITY")
                    if native is None:
                        _fail(3, "MISSING_IDENTITY")
                    native = _text(native, True)
                    if native != source["session"]:
                        _fail(3, "SESSION_MISMATCH")
                    ident = p.get("id")
                    execution = dict(model=_text(p.get("model")), effort=_text(row.get("effort")),
                                     per_turn_effort=_text(row.get("perTurnEffort")),
                                     cli_version=_text(row.get("version")),
                                     session_start_cli_version=None,
                                     model_source="message.model" if p.get("model") is not None else None,
                                     effort_source="assistant.effort" if row.get("effort") is not None else None,
                                     parent_session=_text(parent) if sidechain is True else None)
                    if sidechain is True and parent is not None:
                        if claude_parent is not None and parent != claude_parent:
                            _fail(5, "SESSION_CONFLICT")
                        claude_parent = parent
                else:
                    p = row.get("payload")
                    if not isinstance(p, dict):
                        _fail(5, "BAD_RECORD")
                    if p.get("thread_id") is None or p.get("session_id") is None:
                        _fail(3, "MISSING_IDENTITY")
                    native = _text(p.get("thread_id"), True)
                    if native != p.get("session_id"):
                        _fail(5, "SESSION_CONFLICT")
                    values, positive = _usage(p.get("usage", {}), fmt)
                    ident = p.get("response_id")
                    turn = _text(p.get("turn_id"))
                    ctx = contexts.get(turn, {})
                    execution = dict(model=ctx.get("model"), effort=ctx.get("effort"),
                                     per_turn_effort=None, cli_version=None,
                                     session_start_cli_version=None,
                                     model_source="turn_context" if ctx else None,
                                     effort_source="turn_context" if ctx else None, parent_session=None)
                    if native == primary and "thread_token_usage" in p:
                        final, _ = _usage(p["thread_token_usage"], "codex")
                        info["counter_line"] = line
                if not isinstance(ident, str) or not ident.strip():
                    _fail(5, "MISSING_CALL_ID")
                call_id = _digest([fmt, native, ident])
                identities.add(call_id)
                if len(identities) > limits["max_calls"]:
                    _fail(3, "CALL_LIMIT")
                collision = _digest([fmt, ident])
                call = Call(call_id, collision, native, _stamp(row.get("timestamp")), values,
                            execution, dict(source_index=index, first_line=line, last_line=line,
                                            record_count=1), positive)
                if collision in calls:
                    _merge(calls[collision], call, fmt)
                else:
                    calls[collision] = call
    except (FileNotFoundError, PermissionError):
        info.update(state="UNAVAILABLE", reason="SOURCE_UNREADABLE")
        return [], info
    except Refusal as exc:
        if exc.path is None:
            exc.path, exc.line = path, line
        raise
    except UnicodeError:
        _fail(5, "SOURCE_ENCODING", path, line)
    for call in calls.values():
        _invariants(call.values, fmt, path, call.evidence["last_line"])
        if (fmt == "claude" and all(call.values[k] == 0 for k in C_FIELDS)
                and call.positive_iteration):
            _fail(3, "AMBIGUOUS_USAGE", path, call.evidence["first_line"])
    if fmt == "codex":
        if primary is None:
            info.update(state="UNAVAILABLE", reason="MISSING_IDENTITY")
            return [], info
        chain, sid = set(), primary
        while sid is not None:
            if sid in chain:
                _fail(5, "FORK_CYCLE", path)
            if sid not in metas:
                _fail(3, "MISSING_ANCESTRY", path)
            chain.add(sid)
            sid = metas[sid][0]
        if set(metas) != chain or any(c.native not in chain for c in calls.values()):
            _fail(5, "FOREIGN_THREAD", path)
        _reconcile(list(calls.values()), final, info)
        info["replayed_ancestor_records"] = sum(c.evidence["record_count"] for c in calls.values() if c.native != primary)
        calls = {k: c for k, c in calls.items() if c.native == primary}
        for c in calls.values():
            c.execution["session_start_cli_version"] = metas[primary][1]
    info["seen_calls"] = len(calls)
    if not calls:
        info.update(state="UNAVAILABLE", reason="NO_CALLS")
    elif fmt == "codex" and any((c.values["cache_write_input_tokens"] or 0) > 0 for c in calls.values()):
        info["reason"] = "OVERLAP_UNAVAILABLE"
    return list(calls.values()), info


def _totals(calls, unavailable):
    result = {}
    for name in METRICS:
        present = [c["metrics"][name] for c in calls if c["metrics"][name] is not None]
        missing = len(calls) - len(present)
        complete = not missing and not unavailable
        result[name] = dict(value=sum(present) if complete else None,
                            measured_subtotal=sum(present), covered_calls=len(present),
                            missing_calls=missing, unavailable_sources=unavailable,
                            status="AVAILABLE" if complete else "PARTIAL" if present else "UNAVAILABLE")
    return result


def _measure(sources, limits, since, until):
    identities, inodes, global_calls, infos = set(), set(), {}, []
    for i, source in enumerate(sources):
        calls, info = _read_source(source, i, limits, identities, inodes)
        infos.append(info)
        attribution = {k: source[k] for k in ATTRIBUTION}
        for c in calls:
            metrics = _metrics(c.values, source["format"])
            record = dict(id=c.ident, at=c.at.isoformat(), attribution=attribution,
                          execution=c.execution, format=source["format"], metrics=metrics,
                          evidence=c.evidence, duplicate_source_count=0)
            if since <= c.at < until:
                info["selected_calls"] += 1
            signature = (c.native, c.at, c.values, c.execution, attribution)
            if c.collision in global_calls:
                old_signature, old = global_calls[c.collision]
                if signature != old_signature:
                    _fail(5, "CALL_CONFLICT", info["path"])
                old["duplicate_source_count"] += 1
            else:
                global_calls[c.collision] = signature, record
    selected = [r for (_, r) in global_calls.values() if since <= _stamp(r["at"]) < until]
    selected.sort(key=lambda c: (c["at"], c["id"]))
    unavailable = sum(s["state"] == "UNAVAILABLE" for s in infos)
    totals = _totals(selected, unavailable)
    groups = {}
    for c in selected:
        key = json.dumps([c["format"], c["attribution"], c["execution"]], sort_keys=True)
        groups.setdefault(key, []).append(c)
    grouped = [dict(format=rows[0]["format"], attribution=rows[0]["attribution"],
                    execution=rows[0]["execution"], scope="observed_calls",
                    totals=_totals(rows, unavailable)) for _, rows in sorted(groups.items())]
    report = dict(schema="dflow.telemetry/1", window=dict(since=since.isoformat(), until=until.isoformat()),
                  effective_limits=limits | {"max_metadata_chars": METADATA_CHARS},
                  calls=selected, totals=totals, groups=grouped, sources=infos,
                  coverage_scope="provided source files and recognized native record shapes",
                  unavailable={k: "UNAVAILABLE" for k in ("cost", "quota_weighting", "latency", "quality",
                               "provider_auth_mode", "instruction_hashes", "tool_schema", "cache_policy")})
    complete = all(totals[k]["value"] is not None for k in ESSENTIAL)
    return report, complete


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        _fail(2, "USAGE")


def _envelope(ok, state, reason, items, paths=(), command="telemetry"):
    return dict(schema="dflow.result/1", ok=ok, command=command, state=state,
                reason=reason, paths=[str(p) for p in paths], items=items)


def run(argv):
    """Return (one result envelope, exit code). Do not print or create files."""
    path = None
    try:
        if argv in (["--help"], ["-h"], ["telemetry", "--help"], ["telemetry", "-h"]):
            return _envelope(True, "HELP", "HELP", [{
                "usage": "python -B -m dflow telemetry MANIFEST --since ISO --until ISO [--max-record-bytes N] [--max-calls N]",
                "defaults": {"max_record_bytes": DEFAULT_RECORD_BYTES, "max_calls": DEFAULT_CALLS,
                             "max_metadata_chars": METADATA_CHARS}}], command="help"), 0
        parser = _Parser(add_help=False)
        parser.add_argument("command", choices=["telemetry"])
        parser.add_argument("manifest")
        parser.add_argument("--since", required=True)
        parser.add_argument("--until", required=True)
        parser.add_argument("--max-record-bytes", type=int, default=DEFAULT_RECORD_BYTES)
        parser.add_argument("--max-calls", type=int, default=DEFAULT_CALLS)
        args = parser.parse_args(argv)
        if args.max_record_bytes <= 0 or args.max_calls <= 0:
            _fail(2, "USAGE")
        if not sys.platform.startswith("linux"):
            _fail(3, "UNSUPPORTED_PLATFORM")
        since, until = _stamp(args.since, 2), _stamp(args.until, 2)
        if since >= until:
            _fail(2, "INVALID_WINDOW")
        path = Path(args.manifest).absolute()
        limits = dict(max_record_bytes=args.max_record_bytes, max_calls=args.max_calls)
        sources = _manifest(path, args.max_record_bytes)
        report, complete = _measure(sources, limits, since, until)
        result = _envelope(complete, "AVAILABLE" if complete else "PARTIAL",
                           "MEASURED" if complete else "INCOMPLETE_COVERAGE", [report], [path])
        # Aggregates can exceed JSON's integer conversion limit even if each input fits.
        json.dumps(result, separators=(",", ":"), allow_nan=False)
        return result, 0 if complete else 3
    except Refusal as exc:
        return _envelope(False, "REFUSED", exc.reason,
                         [dict(field=exc.field, line=exc.line)],
                         [exc.path] if exc.path is not None else [path] if path else []), exc.code
    except OSError:
        return _envelope(False, "INFRA", "IO_FAILURE", [dict(field=None, line=None)], [path] if path else []), 4
    except Exception:
        return _envelope(False, "INFRA", "INTERNAL_FAILURE", [dict(field=None, line=None)], [path] if path else []), 4
