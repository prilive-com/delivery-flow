"""Hand-counted telemetry witnesses. No private logs or credentials are fixtures."""
import contextlib
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tracemalloc
import unittest
from unittest import mock

from dflow import telemetry

START = "2026-10-01T00:00:00Z"
END = "2026-11-01T00:00:00Z"
AT = "2026-10-15T00:00:00Z"
X = dict(input_tokens=100, cached_input_tokens=60, cache_write_input_tokens=0,
         output_tokens=8, reasoning_output_tokens=3, total_tokens=108)
X2 = dict(input_tokens=40, cached_input_tokens=10, cache_write_input_tokens=0,
          output_tokens=2, reasoning_output_tokens=1, total_tokens=42)
F = dict(input_tokens=140, cached_input_tokens=70, cache_write_input_tokens=0,
         output_tokens=10, reasoning_output_tokens=4, total_tokens=150)
A = dict(input_tokens=20, cached_input_tokens=10, cache_write_input_tokens=0,
         output_tokens=2, reasoning_output_tokens=1, total_tokens=22)
FORK = dict(input_tokens=120, cached_input_tokens=70, cache_write_input_tokens=0,
            output_tokens=10, reasoning_output_tokens=4, total_tokens=130)


def claude(ident="c", session="s", at=AT):
    return {"type": "assistant", "timestamp": at, "sessionId": session,
            "version": "test-cli", "effort": "high", "message": {
                "id": ident, "model": "model-C", "content": "PRIVATE_BODY_276",
                "usage": {"input_tokens": 10, "cache_creation_input_tokens": 20,
                          "cache_read_input_tokens": 30, "output_tokens": 5,
                          "output_tokens_details": {"thinking_tokens": 2}}}}


def meta(session="s", parent=None):
    p = {"id": session, "session_id": session, "cli_version": "start-cli"}
    if parent is not None:
        p["forked_from_id"] = parent
    return {"type": "session_meta", "payload": p}


def context(turn, model, effort="high"):
    return {"type": "turn_context", "payload": {
        "turn_id": turn, "model": model, "effort": effort}}


def codex(ident="x", session="s", usage=None, final=None, turn="t", at=AT):
    return {"type": "token_usage_record", "timestamp": at, "payload": {
        "response_id": ident, "thread_id": session, "session_id": session,
        "turn_id": turn, "usage": copy.deepcopy(X if usage is None else usage),
        "thread_token_usage": copy.deepcopy(X if final is None else final)}}


def fork():
    return [meta("P", "A"), meta("A"), codex("a1", "A", A, A),
            codex("p1", "P", X, FORK)]


class TelemetryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.serial = 0
        self.manifest = self.root / "input.toml"

    def source(self, rows, fmt="claude", session="s", **labels):
        self.serial += 1
        p = self.root / f"source-{self.serial}.jsonl"
        if isinstance(rows, bytes):
            p.write_bytes(rows)
        else:
            p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
        return dict(format=fmt, path=str(p), session=session, project="synthetic-ts",
                    actor="main", slice="slice-1", stage="changes") | labels

    def manifest_bytes(self, sources):
        lines = ['schema = "dflow.telemetry-input/1"']
        for source in sources:
            lines.append("[[source]]")
            for key, value in source.items():
                encoded = json.dumps(value, ensure_ascii=False)
                lines.append(f"{key} = {encoded}")
        return ("\n".join(lines) + "\n").encode()

    def arguments(self, sources, extra=(), since=START, until=END):
        self.manifest.write_bytes(self.manifest_bytes(sources))
        return ["telemetry", str(self.manifest), "--since", since,
                "--until", until, *extra]

    def invoke(self, sources, **kwargs):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            result, code = telemetry.run(self.arguments(sources, **kwargs))
        self.assertEqual((out.getvalue(), err.getvalue()), ("", ""))
        self.assertEqual(result["schema"], "dflow.result/1")
        self.assertEqual(set(result), {"schema", "ok", "command", "state", "reason", "paths", "items"})
        return result, code

    def report(self, sources, **kwargs):
        result, code = self.invoke(sources, **kwargs)
        self.assertEqual(code, 0, result)
        self.assertTrue(result["ok"])
        self.assertEqual(result["items"][0]["schema"], "dflow.telemetry/1")
        return result["items"][0]

    def failure(self, sources, code, reason=None, **kwargs):
        result, actual = self.invoke(sources, **kwargs)
        self.assertEqual(actual, code, result)
        self.assertFalse(result["ok"])
        if reason:
            self.assertEqual(result["reason"], reason)
        self.assertTrue(result["reason"])
        self.assertTrue(result["items"], "failure needs an error detail or a partial report")
        return result

    def test_claude_split_breakdowns_and_zero(self):
        c = claude()
        u = c["message"]["usage"]
        u["iterations"] = [{k: u[k] for k in ("input_tokens", "output_tokens",
                            "cache_creation_input_tokens", "cache_read_input_tokens")}]
        u["cache_creation"] = {"ephemeral_1h_input_tokens": 15, "ephemeral_5m_input_tokens": 5}
        u["server_tool_use"] = {"web_search_requests": 99}
        s = self.source([c, c, {"type": "cost-state", "usage": {"input_tokens": 999}}])
        r = self.report([s])
        self.assertEqual(len(r["calls"]), 1)
        self.assertEqual({k: v["value"] for k, v in r["totals"].items()},
                         dict(fresh_input=10, cache_write_input=20, cache_read_input=30,
                              output=5, thinking=2, raw=65))
        self.assertEqual(r["calls"][0]["evidence"]["record_count"], 2)
        z = claude("zero")
        z["message"]["usage"] = {"input_tokens": 0, "cache_creation_input_tokens": 0,
                                  "cache_read_input_tokens": 0, "output_tokens": 0}
        self.assertEqual(self.report([self.source([z])])["totals"]["raw"]["value"], 0)

    def test_merge_before_thinking_subset(self):
        a, b = claude(), claude()
        a["message"]["usage"]["output_tokens"] = 1
        self.assertEqual(self.report([self.source([a, b])])["totals"]["raw"]["value"], 65)
        b["message"]["usage"]["output_tokens_details"]["thinking_tokens"] = 6
        self.failure([self.source([a, b])], 5)

    def test_missing_essentials_never_success(self):
        for key, metric in [("input_tokens", "fresh_input"),
                            ("cache_creation_input_tokens", "cache_write_input"),
                            ("cache_read_input_tokens", "cache_read_input"),
                            ("output_tokens", "output")]:
            with self.subTest(key=key):
                c = claude()
                del c["message"]["usage"][key]
                result = self.failure([self.source([c])], 3)
                r = result["items"][0]
                self.assertIsNone(r["totals"][metric]["value"])
                self.assertEqual(r["totals"][metric]["missing_calls"], 1)
                self.assertIsNone(r["totals"]["raw"]["value"])
        c = claude()
        del c["message"]["usage"]["output_tokens_details"]
        r = self.report([self.source([c])])
        self.assertIsNone(r["totals"]["thinking"]["value"])
        self.assertEqual(r["totals"]["raw"]["value"], 65)

    def test_partial_metric_has_subtotal_not_total(self):
        c, d = claude("c"), claude("d")
        del d["message"]["usage"]["cache_read_input_tokens"]
        r = self.failure([self.source([c, d])], 3)["items"][0]
        v = r["totals"]["cache_read_input"]
        self.assertEqual((v["value"], v["measured_subtotal"], v["covered_calls"], v["missing_calls"]),
                         (None, 30, 1, 1))

    def test_bad_counter_classes_and_subset(self):
        for value in [-1, True, 1.0, "10"]:
            with self.subTest(value=value):
                c = claude()
                c["message"]["usage"]["input_tokens"] = value
                self.failure([self.source([c])], 5)
        for value in [-1, True, 1.0]:
            c = claude()
            c["message"]["usage"]["output_tokens_details"]["thinking_tokens"] = value
            self.failure([self.source([c])], 5)
        for change in [{"cached_input_tokens": 101}, {"reasoning_output_tokens": 9},
                       {"total_tokens": 999}]:
            bad = X | change
            self.failure([self.source([meta(), codex(usage=bad, final=bad)], "codex")], 5)

    def test_synthetic_and_ambiguous_iterations(self):
        c = claude()
        c["message"]["model"] = "<synthetic>"
        self.failure([self.source([c])], 3, "SYNTHETIC_USAGE")
        c["message"]["usage"] = {k: 0 for k in ["input_tokens", "cache_creation_input_tokens",
                                                  "cache_read_input_tokens", "output_tokens"]}
        r = self.report([self.source([c, claude("real")])])
        self.assertEqual(len(r["calls"]), 1)
        c = claude()
        c["message"]["usage"] = dict(input_tokens=0, cache_creation_input_tokens=0,
                                       cache_read_input_tokens=0, output_tokens=0,
                                       iterations=[{"input_tokens": 1}])
        self.failure([self.source([c])], 3, "AMBIGUOUS_USAGE")

    def test_codex_increments_and_ignored_counters(self):
        rows = [meta(), codex(), {"type": "event_msg", "payload": {
            "type": "token_count", "info": {"total_token_usage": {"total_tokens": 999999}}}},
            {"type": "compacted", "payload": {"latest_token_usage_record": codex()["payload"]}},
            codex("x2", usage=X2, final=F), codex("x2", usage=X2, final=F)]
        r = self.report([self.source(rows, "codex")])
        self.assertEqual(len(r["calls"]), 2)
        self.assertEqual(r["totals"]["raw"]["value"], 150)
        self.assertEqual(r["totals"]["fresh_input"]["value"], 70)
        self.assertEqual(r["totals"]["thinking"]["value"], 4)
        self.assertEqual(r["sources"][0]["reconciliation"], "MATCH")
        bad = rows + [codex("x2", usage=X2 | {"output_tokens": 3, "total_tokens": 43}, final=F)]
        self.failure([self.source(bad, "codex")], 5)

    def test_reconcile_all_fields_and_deleted_call(self):
        good = [meta(), codex(), codex("x2", usage=X2, final=F)]
        self.assertEqual(self.report([self.source(good, "codex")])["totals"]["raw"]["value"], 150)
        self.failure([self.source([good[0], good[2]], "codex")], 5, "COUNTER_MISMATCH")
        bad = copy.deepcopy(good)
        bad[-1]["payload"]["thread_token_usage"]["cached_input_tokens"] = 69
        self.failure([self.source(bad, "codex")], 5, "COUNTER_MISMATCH")
        bad[-1]["payload"]["thread_token_usage"].pop("cached_input_tokens")
        r = self.failure([self.source(bad, "codex")], 3)["items"][0]
        self.assertIsNone(r["totals"]["raw"]["value"])
        self.assertEqual(r["totals"]["raw"]["measured_subtotal"], 150)

    def test_error_locations_point_to_source_and_counter_row(self):
        c = claude()
        c["message"]["usage"]["output_tokens_details"]["thinking_tokens"] = 6
        source = self.source([c])
        result = self.failure([source], 5)
        self.assertEqual(result["paths"], [source["path"]])
        self.assertEqual(result["items"][0]["line"], 1)
        final = F | {"cached_input_tokens": 69}
        source = self.source([meta(), codex(), codex("x2", usage=X2, final=final)], "codex")
        result = self.failure([source], 5, "COUNTER_MISMATCH")
        self.assertEqual(result["paths"], [source["path"]])
        self.assertEqual(result["items"][0]["line"], 3)
        self.assertEqual(result["items"][0]["field"], "cached_input_tokens")

    def test_codex_missing_fields_and_write_overlap(self):
        for key in ["input_tokens", "cached_input_tokens", "cache_write_input_tokens", "output_tokens"]:
            row = codex()
            del row["payload"]["usage"][key]
            self.failure([self.source([meta(), row], "codex")], 3)
        row = codex()
        row["payload"].pop("thread_token_usage")
        self.failure([self.source([meta(), row], "codex")], 3)
        for total in [108, 110]:
            u = X | {"cache_write_input_tokens": 2, "total_tokens": total}
            r = self.failure([self.source([meta(), codex(usage=u, final=u)], "codex")], 3)["items"][0]
            self.assertEqual(r["calls"][0]["metrics"]["cache_write_input"], 2)
            self.assertIsNone(r["calls"][0]["metrics"]["raw"])

    def test_fork_counter_and_no_rebilling(self):
        r = self.report([self.source(fork(), "codex", "P")])
        self.assertEqual((len(r["calls"]), r["totals"]["raw"]["value"]), (1, 108))
        self.assertEqual(r["sources"][0]["replayed_ancestor_records"], 1)
        bad = fork()
        bad.pop(2)
        self.failure([self.source(bad, "codex", "P")], 5, "COUNTER_MISMATCH")
        original = self.source([meta("A"), codex("a1", "A", A, A)], "codex", "A")
        r = self.report([original, self.source(fork(), "codex", "P")])
        self.assertEqual((len(r["calls"]), r["totals"]["raw"]["value"]), (2, 130))

    def test_fork_invalid_ancestry(self):
        missing = fork()
        missing.pop(1)
        self.failure([self.source(missing, "codex", "P")], 3)
        cycle = fork()
        cycle[1] = meta("A", "P")
        self.failure([self.source(cycle, "codex", "P")], 5)
        foreign = fork()
        foreign[0] = meta("P")
        self.failure([self.source(foreign, "codex", "P")], 5)
        foreign = fork() + [meta("foreign")]
        self.failure([self.source(foreign, "codex", "P")], 5)

    def test_budget_includes_ancestors_without_competing_cap(self):
        self.report([self.source(fork(), "codex", "P")], extra=["--max-calls", "2"])
        second = dict(input_tokens=1, cached_input_tokens=0, cache_write_input_tokens=0,
                      output_tokens=1, reasoning_output_tokens=0, total_tokens=2)
        final = dict(input_tokens=121, cached_input_tokens=70, cache_write_input_tokens=0,
                     output_tokens=11, reasoning_output_tokens=4, total_tokens=132)
        rows = fork()
        rows.insert(3, codex("a2", "A", second, A | {"input_tokens": 21,
                    "output_tokens": 3, "total_tokens": 24}))
        rows[-1]["payload"]["thread_token_usage"] = final
        s = self.source(rows, "codex", "P")
        self.failure([s], 3, "CALL_LIMIT", extra=["--max-calls", "2"])
        self.assertEqual(self.report([s], extra=["--max-calls", "3"])["totals"]["raw"]["value"], 108)

    def test_budget_across_sources_and_duplicates(self):
        a = self.source([claude("a1", "A"), claude("a2", "A")], session="A")
        b = self.source([claude("b1", "B")], session="B", project="docs-repo")
        self.failure([a, b], 3, "CALL_LIMIT", extra=["--max-calls", "2"])
        one = self.source([claude("a1", "A")], session="A")
        self.assertEqual(self.report([one, b], extra=["--max-calls", "2"])["totals"]["raw"]["value"], 130)
        c = claude()
        self.report([self.source([c, c])], extra=["--max-calls", "1"])

    def test_metadata_map_limits_are_separate(self):
        for n, expected in [(2, 0), (3, 3)]:
            with self.subTest(kind="contexts", count=n):
                s = self.source([meta(), *[context(str(i), "m") for i in range(n)], codex()], "codex")
                if expected:
                    self.failure([s], 3, "CONTEXT_LIMIT", extra=["--max-calls", "2"])
                else:
                    self.report([s], extra=["--max-calls", "2"])
            with self.subTest(kind="metas", count=n):
                rows = [meta("P", "A"), meta("A", "B" if n == 3 else None)]
                if n == 3:
                    rows.append(meta("B"))
                rows.append(codex("p", "P"))
                s = self.source(rows, "codex", "P")
                if expected:
                    self.failure([s], 3, "METADATA_LIMIT", extra=["--max-calls", "2"])
                else:
                    self.report([s], extra=["--max-calls", "2"])

    def test_metadata_value_characters_not_bytes(self):
        for field in ["model", "effort", "version"]:
            for n in [512, 513]:
                with self.subTest(field=field, n=n):
                    c = claude()
                    target = c["message"] if field == "model" else c
                    target[field] = "🧪" * n
                    s = self.source([c])
                    if n == 513:
                        self.failure([s], 3, "METADATA_VALUE_LIMIT")
                    else:
                        r = self.report([s])
                        key = "cli_version" if field == "version" else field
                        self.assertEqual(r["calls"][0]["execution"][key], "🧪" * 512)

    def test_unknown_record_with_any_supported_token_counter(self):
        for field in ["input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens",
                      "output_tokens", "cached_input_tokens", "cache_write_input_tokens",
                      "reasoning_output_tokens", "total_tokens", "thinking_tokens", "future_tokens"]:
            with self.subTest(field=field):
                s = self.source([claude(), {"type": "new-accounting", field: 100}])
                self.failure([s], 3, "UNKNOWN_ACCOUNTING")

    def test_unsupported_usage_token_fields(self):
        for fmt in ["claude", "codex"]:
            for field, value in [("thinking_tokens", -1), ("thinking_tokens", True),
                                 ("thinking_tokens", "bad"), ("thinking_tokens", 50),
                                 ("future_tokens", 1)]:
                with self.subTest(fmt=fmt, field=field, value=value):
                    row = claude() if fmt == "claude" else codex()
                    usage = row["message" if fmt == "claude" else "payload"]["usage"]
                    usage[field] = value
                    rows = [row] if fmt == "claude" else [meta(), row]
                    self.failure([self.source(rows, fmt)], 3, "UNKNOWN_ACCOUNTING")

    def test_unknown_nested_token_fields_and_positions(self):
        for container in ["iterations", "output_tokens_details", "cache_creation", "opaque"]:
            for value in [10, 0]:
                with self.subTest(container=container, value=value):
                    c = claude()
                    nested = {"future_tokens": value}
                    c["message"]["usage"][container] = [nested] if container == "iterations" else nested
                    self.failure([self.source([c])], 3, "UNKNOWN_ACCOUNTING")
        for value in [10, 0]:
            with self.subTest(zero_parent=value):
                c = claude()
                c["message"]["usage"] = dict(input_tokens=0, output_tokens=0,
                    cache_read_input_tokens=0, cache_creation_input_tokens=0,
                    iterations=[{"future_tokens": value}])
                self.failure([self.source([c])], 3, "UNKNOWN_ACCOUNTING")
        for fmt in ["claude", "codex"]:
            with self.subTest(misplaced=fmt):
                c = claude() if fmt == "claude" else codex()
                c["message" if fmt == "claude" else "payload"]["usage"]["opaque"] = {"input_tokens": 10}
                rows = [c] if fmt == "claude" else [meta(), c]
                self.failure([self.source(rows, fmt)], 3, "UNKNOWN_ACCOUNTING")

        for container, nested in [("iterations", [{"input_tokens": 1}]),
                                  ("output_tokens_details", {"thinking_tokens": 1}),
                                  ("cache_creation", {"ephemeral_1h_input_tokens": 1})]:
            with self.subTest(codex_container=container):
                c = codex()
                c["payload"]["usage"][container] = nested
                self.failure([self.source([meta(), c], "codex")], 3, "UNKNOWN_ACCOUNTING")

    def test_nested_ephemeral_breakdowns_are_valid_not_extra_spend(self):
        c = claude()
        breakdown = {"ephemeral_1h_input_tokens": 15, "ephemeral_5m_input_tokens": 5}
        u = c["message"]["usage"]
        u["cache_creation"] = copy.deepcopy(breakdown)
        u["iterations"] = [{"input_tokens": 1, "output_tokens": 1,
                            "cache_creation": copy.deepcopy(breakdown)}]
        self.assertEqual(self.report([self.source([c])])["totals"]["raw"]["value"], 65)
        for field in breakdown:
            with self.subTest(misplaced=field):
                wrong = claude()
                wrong["message"]["usage"]["output_tokens_details"][field] = 1
                self.failure([self.source([wrong])], 3, "UNKNOWN_ACCOUNTING")
            for value in [-1, True, "bad", 0.5]:
                with self.subTest(field=field, value=value):
                    wrong = copy.deepcopy(c)
                    wrong["message"]["usage"]["iterations"][0]["cache_creation"][field] = value
                    self.failure([self.source([wrong])], 5, "BAD_COUNTER")

    def test_all_iteration_counters_checked_after_positive_input(self):
        c = claude()
        c["message"]["usage"]["iterations"] = [{"input_tokens": 1, "output_tokens": 1}]
        self.assertEqual(self.report([self.source([c])])["totals"]["raw"]["value"], 65)
        for field in ["cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens"]:
            for value in [-1, True, "bad", 0.5]:
                with self.subTest(field=field, value=value):
                    c["message"]["usage"]["iterations"] = [{"input_tokens": 1, field: value}]
                    self.failure([self.source([c])], 5, "BAD_COUNTER")

    def test_child_parent_identity_is_consistent_across_calls(self):
        rows = [claude("first", "parent-A"), claude("second", "parent-A")]
        for row in rows:
            row.update(agentId="child", isSidechain=True)
        self.assertEqual(self.report([self.source(rows, session="child")])["totals"]["raw"]["value"], 130)
        rows[1]["sessionId"] = "parent-B"
        self.failure([self.source(rows, session="child")], 5, "SESSION_CONFLICT")

    def test_duplicate_known_execution_metadata_conflicts(self):
        for model, effort in [("model-B", "high"), ("model-A", "low")]:
            with self.subTest(model=model, effort=effort):
                rows = [meta(), context("t", "model-A", "high"), codex(),
                        context("t", model, effort), codex()]
                self.failure([self.source(rows, "codex")], 5, "CALL_CONFLICT")

    def test_duplicate_call_cannot_backfill_future_context(self):
        rows = [meta(), codex(), context("t", "future-model", "low"), codex()]
        r = self.report([self.source(rows, "codex")])
        self.assertEqual(len(r["calls"]), 1)
        self.assertEqual(r["totals"]["raw"]["value"], 108)
        execution = r["calls"][0]["execution"]
        for field in ["model", "effort", "model_source", "effort_source"]:
            self.assertIsNone(execution[field])

    def test_aggregate_serialization_failure_stays_in_envelope(self):
        rows = [claude("huge-a"), claude("huge-b")]
        for row in rows:
            row["message"]["usage"]["input_tokens"] = 10 ** 4300 - 1
        args = self.arguments([self.source(rows)])
        result, code = telemetry.run(args)
        self.assertEqual((code, result["reason"], result["ok"]), (4, "INTERNAL_FAILURE", False))
        p = subprocess.run([sys.executable, "-B", "-m", "dflow", *args],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 4)
        self.assertEqual(p.stderr, "")
        self.assertEqual(len(p.stdout.splitlines()), 1)
        self.assertEqual(json.loads(p.stdout), result)

    def test_multiturn_metadata_and_unknown_future_context(self):
        third = dict(input_tokens=0, cached_input_tokens=0, cache_write_input_tokens=0,
                     output_tokens=1, reasoning_output_tokens=0, total_tokens=1)
        final = F | {"output_tokens": 11, "total_tokens": 151}
        rows = [meta(), context("A", "model-A"), codex(turn="A"),
                context("B", "model-B", "medium"), codex("x2", usage=X2, final=F, turn="B"),
                context("D", "unrelated"), codex("x3", usage=third, final=final, turn="C"),
                context("C", "future")]
        r = self.report([self.source(rows, "codex")])
        by_model = {c["execution"]["model"]: c for c in r["calls"]}
        self.assertEqual(set(by_model), {"model-A", "model-B", None})
        self.assertEqual(by_model["model-A"]["execution"]["effort"], "high")
        self.assertEqual(by_model["model-B"]["execution"]["effort"], "medium")
        self.assertEqual(by_model["model-A"]["execution"]["model_source"], "turn_context")
        for c in r["calls"]:
            self.assertIsNone(c["execution"]["cli_version"])
            self.assertEqual(c["execution"]["session_start_cli_version"], "start-cli")
        self.assertEqual(sorted(g["totals"]["raw"]["value"] for g in r["groups"]), [1, 42, 108])

    def test_window_full_merge_before_filter_and_offsets(self):
        a, b = claude(at="2026-10-15T00:59:59Z"), claude(at="2026-10-15T01:00:01Z")
        a["message"]["usage"]["output_tokens"] = 1
        a["message"]["usage"]["output_tokens_details"]["thinking_tokens"] = 0
        s = self.source([a, b])
        r = self.report([s], since="2026-10-15T00:00:00Z", until="2026-10-15T01:00:00Z")
        self.assertEqual(r["calls"][0]["metrics"]["output"], 5)
        self.assertEqual(r["calls"][0]["metrics"]["thinking"], 2)
        self.assertEqual(r["totals"]["raw"]["value"], 65)
        r = self.report([s], since="2026-10-15T01:00:00Z", until="2026-10-15T02:00:00Z")
        self.assertEqual((len(r["calls"]), r["totals"]["raw"]["value"]), (0, 0))
        c = claude(at="2026-10-15T01:30:00+01:00")
        self.assertEqual(len(self.report([self.source([c])], since="2026-10-15T00:30:00Z",
                                        until="2026-10-15T00:30:01Z")["calls"]), 1)
        self.assertEqual(len(self.report([self.source([c])], since="2026-10-15T00:00:00Z",
                                        until="2026-10-15T00:30:00Z")["calls"]), 0)

    def test_invalid_timestamp_outside_window(self):
        for stamp in [None, "2020-01-01", "bad", "PRIVATE_BODY_276", 0]:
            result = self.failure([self.source([claude(at=stamp)])], 5)
            self.assertNotIn("PRIVATE_BODY_276", json.dumps(result))
        self.failure([self.source([claude()])], 2, since=END, until=START)
        self.failure([self.source([claude()])], 2, since="2026-10-01")

    def test_child_identity_and_aliases(self):
        c = claude(session="parent")
        c.update(agentId="child", isSidechain=True)
        child = self.report([self.source([c], session="child")])
        self.assertEqual(child["totals"]["raw"]["value"], 65)
        self.assertEqual(child["calls"][0]["execution"]["parent_session"], "parent")
        main = self.report([self.source([claude()])])
        self.assertIsNone(main["calls"][0]["execution"]["parent_session"])
        self.failure([self.source([c], session="parent")], 3, "SESSION_MISMATCH")
        c.pop("agentId")
        self.failure([self.source([c], session="parent")], 3)
        c = claude()
        c["session_id"] = "different"
        self.failure([self.source([c])], 5)
        self.failure([self.source([claude()], session="wrong")], 3, "SESSION_MISMATCH")
        self.failure([self.source([meta(), codex()], "codex", session="wrong")], 3, "SESSION_MISMATCH")

    def test_crosssource_copy_dedup_and_conflicts(self):
        a, b = self.source([claude()]), self.source([claude()])
        r = self.report([a, b])
        self.assertEqual((len(r["calls"]), r["totals"]["raw"]["value"]), (1, 65))
        self.assertEqual(r["calls"][0]["duplicate_source_count"], 1)
        for change in ["counter", "metadata", "timestamp", "attribution", "session"]:
            with self.subTest(change=change):
                c = claude()
                labels = {}
                if change == "counter":
                    c["message"]["usage"]["output_tokens"] = 6
                elif change == "metadata":
                    c["message"]["model"] = "different"
                elif change == "timestamp":
                    c["timestamp"] = "2026-10-16T00:00:00Z"
                elif change == "attribution":
                    labels["actor"] = "reviewer"
                else:
                    c["sessionId"] = "different"
                    labels["session"] = "different"
                self.failure([a, self.source([c], **labels)], 5)

    def test_alias_files_relative_symlink_hardlink(self):
        s = self.source([claude()])
        p = Path(s["path"])
        for alias in [p.name, "./" + p.name, "symlink.jsonl", "hardlink.jsonl"]:
            if alias.startswith("symlink"):
                (self.root / alias).symlink_to(p)
            if alias.startswith("hardlink"):
                os.link(p, self.root / alias)
            self.failure([s, s | {"path": alias}], 3, "SOURCE_ALIAS")
        self.assertEqual(self.report([s | {"path": p.name}])["totals"]["raw"]["value"], 65)
        missing = s | {"path": str(self.root / "absent.jsonl")}
        self.failure([missing, missing], 3, "SOURCE_ALIAS")

    def test_missing_source_and_restoration(self):
        good = self.source([claude()])
        missing = good | {"path": str(self.root / "missing.jsonl")}
        r = self.failure([good, missing], 3)["items"][0]
        self.assertIsNone(r["totals"]["raw"]["value"])
        self.assertEqual(r["totals"]["raw"]["measured_subtotal"], 65)
        self.assertEqual(r["totals"]["raw"]["unavailable_sources"], 1)
        Path(missing["path"]).write_text(json.dumps(claude("restored")) + "\n")
        self.assertEqual(self.report([missing])["totals"]["raw"]["value"], 65)
        self.failure([self.source([])], 3)

    def test_json_framing_shapes_and_unknown_accounting(self):
        for data in [b'{"x":1}', b'{"x":1,"x":2}\n', b'{"x":NaN}\n',
                     b'{"x":1e999}\n', b'[]\n', b'{"PRIVATE_BODY_276":\n', b'\xff\n']:
            with self.subTest(data=data):
                if data.endswith(b"\n"):
                    self.failure([self.source(data + (json.dumps(claude()) + "\n").encode())], 5)
                r = self.failure([self.source(data)], 5)
                self.assertNotIn("PRIVATE_BODY_276", json.dumps(r))
        self.failure([self.source([{"type": "new-accounting", "usage": {"input_tokens": 1}}])],
                     3, "UNKNOWN_ACCOUNTING")
        self.failure([self.source([claude(), {"type": "new-accounting", "usage": {"input_tokens": 1}}])],
                     3, "UNKNOWN_ACCOUNTING")
        c = claude()
        c["message"]["content"] = "a\u2028b\u0085c"
        self.assertEqual(self.report([self.source([c])])["totals"]["raw"]["value"], 65)

    def test_manifest_validation_and_native_syntax_line(self):
        s = self.source([claude()])
        for bad in [s | {"actor": "wrong"}, s | {"unknown": "PRIVATE_BODY_276"},
                    {k: v for k, v in s.items() if k != "session"}, s | {"format": True}]:
            r = self.failure([bad], 2)
            self.assertNotIn("PRIVATE_BODY_276", json.dumps(r))
        args = self.arguments([s])
        self.manifest.write_text('schema = "dflow.telemetry-input/2"\n')
        self.assertEqual(telemetry.run(args)[1], 2)
        self.manifest.write_text('schema = "dflow.telemetry-input/1"\n@PRIVATE_BODY_276\n')
        r, code = telemetry.run(args)
        self.assertEqual((code, r["reason"]), (2, "TOML_SYNTAX"))
        self.assertEqual(r["items"][0]["line"], 2 if sys.version_info >= (3, 14) else None)
        self.assertNotIn("PRIVATE_BODY_276", json.dumps(r))

    def test_source_changes_are_real_file_changes(self):
        original = json.loads
        for action in ["append", "rewrite", "replace", "unlink"]:
            with self.subTest(action=action):
                s = self.source([claude(), claude("two")])
                p, done = Path(s["path"]), []
                data = p.read_bytes()
                def decode(*args, **kwargs):
                    value = original(*args, **kwargs)
                    if not done:
                        done.append(True)
                        if action == "append":
                            with p.open("ab") as f:
                                f.write(b'{}\n')
                        elif action == "rewrite":
                            before = p.stat()
                            p.write_bytes(data)
                            os.utime(p, ns=(before.st_atime_ns, before.st_mtime_ns + 1000000000))
                        elif action == "replace":
                            q = self.root / "new-file"
                            q.write_bytes(data)
                            q.replace(p)
                        else:
                            p.unlink()
                    return value
                with mock.patch.object(json, "loads", side_effect=decode):
                    self.failure([s], 3, "SOURCE_CHANGED")
                self.assertTrue(done)

    def test_no_writes_and_repeatable_result(self):
        s = self.source([claude()])
        p = Path(s["path"])
        before = p.read_bytes()
        a, b = self.report([s]), self.report([s])
        self.assertEqual(a, b)
        self.assertEqual(p.read_bytes(), before)
        self.assertEqual(a["sources"][0]["sha256"], hashlib.sha256(before).hexdigest())
        text = json.dumps(a)
        self.assertNotIn("PRIVATE_BODY_276", text)
        self.assertNotIn('"content"', text)
        self.assertEqual(a["unavailable"]["cost"], "UNAVAILABLE")

    def test_call_id_has_one_canonical_unicode_hash(self):
        row = codex("id:2", "sess,1")
        r = self.report([self.source([meta("sess,1"), row], "codex", "sess,1")])
        self.assertEqual(r["calls"][0]["id"],
                         "a19904eda231332b941706a07da7cb2e158a4b37f21fe538154ddd7de218268b")
        c = claude("call-漢", "sess-é")
        r = self.report([self.source([c], session="sess-é")])
        expected = hashlib.sha256('["claude","sess-é","call-漢"]'.encode()).hexdigest()
        self.assertEqual(r["calls"][0]["id"], expected)
        ids = []
        for sess, ident in [("ab", "c"), ("a", "bc")]:
            ids.append(self.report([self.source([claude(ident, sess)], session=sess)])["calls"][0]["id"])
        self.assertNotEqual(*ids)
        c = claude("PRIVATE_BODY_276")
        self.assertNotIn("PRIVATE_BODY_276", json.dumps(self.report([self.source([c])])) )

    def test_known_container_shapes_are_not_falsey_defaults(self):
        for value in [False, 0, "bad", []]:
            c = claude()
            c["message"]["usage"]["output_tokens_details"] = value
            self.failure([self.source([c])], 5)
        for value in [False, 0, "bad", {}]:
            c = claude()
            c["message"]["usage"]["iterations"] = value
            self.failure([self.source([c])], 3)
        for value in [[], {}, True, 1]:
            self.failure([self.source([{"type": value}])], 5)
        for value in [0, 1, "false", []]:
            c = claude()
            c["isSidechain"] = value
            self.failure([self.source([c])], 5)

    def test_missing_native_identity_and_null_alias(self):
        c = claude()
        c["session_id"] = c["sessionId"]
        c["sessionId"] = None
        self.assertEqual(self.report([self.source([c])])["totals"]["raw"]["value"], 65)
        for key in ["id", "thread_id", "session_id"]:
            rows = [meta(), codex()]
            target = rows[0]["payload"] if key == "id" else rows[1]["payload"]
            target.pop(key)
            self.failure([self.source(rows, "codex")], 3)

    def test_absent_metadata_has_no_provenance_claim(self):
        c = claude()
        c["message"].pop("model")
        c.pop("effort")
        e = self.report([self.source([c])])["calls"][0]["execution"]
        self.assertIsNone(e["model"])
        self.assertIsNone(e["model_source"])
        self.assertIsNone(e["effort_source"])

    def test_real_cli_envelopes_and_relative_path_from_other_cwd(self):
        s = self.source([claude()])
        args = self.arguments([s | {"path": Path(s["path"]).name}])
        repo = Path(__file__).resolve().parents[1]
        bad_manifest = self.root / "bad.toml"
        bad_manifest.write_bytes(self.manifest_bytes([self.source(b'{"PRIVATE_BODY_276":\n')]))
        bad_args = list(args)
        bad_args[1] = str(bad_manifest)
        missing_args = list(args)
        missing_args[1] = str(self.root / "absent-manifest.toml")
        cases = [(args, 0), (bad_args, 5), (missing_args, 4), (["--help"], 0), (["--PRIVATE_BODY_276"], 2), ([], 2),
                 (args + ["--max-calls", "0"], 2)]
        for argv, expected in cases:
            with self.subTest(argv=argv):
                p = subprocess.run([sys.executable, "-B", "-m", "dflow", *argv], cwd="/",
                                   env={**os.environ, "PYTHONPATH": str(repo)},
                                   capture_output=True, text=True, timeout=10)
                self.assertEqual(p.returncode, expected, p.stdout + p.stderr)
                self.assertEqual(p.stderr, "")
                self.assertEqual(len(p.stdout.splitlines()), 1)
                d = json.loads(p.stdout)
                self.assertEqual(d["schema"], "dflow.result/1")
                self.assertNotIn("PRIVATE_BODY_276", p.stdout)

    def test_fifo_and_device_refused_without_blocking(self):
        p = self.root / "fifo"
        os.mkfifo(p)
        for path in [p, Path("/dev/null"), self.root]:
            args = self.arguments([dict(self.source([claude()]), path=str(path))])
            proc = subprocess.run([sys.executable, "-B", "-m", "dflow", *args],
                                  capture_output=True, text=True, timeout=5)
            self.assertEqual(proc.returncode, 3, proc.stdout + proc.stderr)
            self.assertEqual(json.loads(proc.stdout)["reason"], "NOT_REGULAR")

    def test_record_limits_defaults_and_overrides(self):
        s = self.source([claude()])
        r = self.report([s])
        self.assertEqual(r["effective_limits"]["max_calls"], 100000)
        self.assertEqual(r["effective_limits"]["max_record_bytes"], 16777216)
        for size, code in [(16777216, 0), (16777217, 3)]:
            prefix, suffix = b'{"type":"user","text":"', b'"}\n'
            data = prefix + b'x' * (size - len(prefix) - len(suffix)) + suffix
            c = self.source(data + (json.dumps(claude()) + "\n").encode())
            if code:
                self.failure([c], 3, "RECORD_LIMIT")
                self.report([c], extra=["--max-record-bytes", "16777217"])
            else:
                self.report([c])

    def test_streaming_memory_and_bounded_duplicate_refs(self):
        sources = []
        prefix, suffix = b'{"type":"user","text":"', b'"}\n'
        row = prefix + b'x' * (1024 - len(prefix) - len(suffix)) + suffix
        for count in [1000, 10000]:
            sources.append(self.source(row * count + (json.dumps(claude()) + "\n").encode()))
        peaks = []
        for s in sources:
            tracemalloc.start()
            try:
                r = self.report([s], extra=["--max-record-bytes", "4096"])
                peaks.append(tracemalloc.get_traced_memory()[1])
            finally:
                tracemalloc.stop()
            self.assertEqual(r["totals"]["raw"]["value"], 65)
        self.assertLessEqual(peaks[1], peaks[0] + 2097152, peaks)
        c = claude()
        r = self.report([self.source([c] * 1000)])
        self.assertEqual(r["calls"][0]["evidence"]["record_count"], 1000)
        self.assertFalse(any(isinstance(v, list) for v in r["calls"][0]["evidence"].values()))


if __name__ == "__main__":
    unittest.main()
