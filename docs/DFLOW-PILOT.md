# dflow: a read-only measurement pilot

This is the first, optional part of dflow. It reads saved Claude and Codex logs
and reports token volume. Run it from this checkout. The declared interpreter is
Python **3.15.2**. The same basic TOML inputs are also tested on Python 3.12.3.
The code uses the Python standard library on Linux.

This reader is a subset of the supplied dflow revision 5 proposal. The active
Delivery Flow now includes the [execution and measurement procedure](DFLOW-INTEGRATION.md).
The shared instruction rollout is part of that update. The execution engine and
new owner-approval/security mechanisms remain separate work; they are not implied
by the reader or the instruction update.

## Run it

See the command help:

```sh
python3.15 -B -m dflow --help
```

Create a private TOML manifest. Replace the paths and native IDs in this example.
Labels such as project, slice and stage are your attribution. They are not read
from the prompt and are not authenticated by the tool.

```toml
schema = "dflow.telemetry-input/1"

[[source]]
format = "claude"
path = "/private/logs/main.jsonl"
project = "my-project"
actor = "main"
session = "native-main-session-id"
slice = "my-slice"
stage = "implementation"

[[source]]
format = "codex"
path = "/private/logs/reviewer.jsonl"
project = "my-project"
actor = "reviewer"
session = "native-codex-session-id"
slice = "my-slice"
stage = "changes"
```

Every source needs every field above. `actor` is `main`, `reviewer` or `other`.
Relative log paths start at the manifest's directory. A main Claude transcript
uses its native `sessionId` (or `session_id`). A child transcript uses `agentId`;
its parent `sessionId` is a different ID. A known child parent must stay the same
across calls in one source. A Codex rollout uses the **first**
`session_meta.payload.id`. Do not use a later ancestor's ID in a forked log.

Run the report with an explicit time range:

```sh
python3.15 -B -m dflow telemetry /private/input.toml --since 2026-10-01T00:00:00Z --until 2026-10-29T00:00:00Z
```

The start is included. The end is excluded. Dates need a time and a UTC offset.
Calls use their earliest observed record time, after all their split records have
been merged. This time is not claimed to be the server's request start time.

The command prints one JSON object on one line, including for help and handled
errors. It creates no report or state files itself. For large inputs, redirect
stdout to a private file and read its `items[0].totals` first. Keep the full file
when later work needs call or source details. Reports contain paths and labels;
check them before sharing them. Raw prompt text and raw call IDs are not output.

`run(argv)` in `dflow.telemetry` returns `(result, exit_code)` without printing.
The module command prints that result. This is the only public Python entry.

## What is counted

| format | one call | fresh input | raw volume |
|---|---|---|---|
| Claude | one native `message.id`; split rows use per-field maxima | `input_tokens` | fresh + cache creation + cache read + output |
| Codex | one native `response_id` and its incremental `usage` | input minus cached input | input + output for the observed zero-cache-write shape |

Thinking and reasoning are parts of output. They are not added again. Claude
iteration details, cache lifetime parts, and server-tool request counts are not
extra tokens. A zero parent usage with positive iteration usage is refused as
ambiguous. Explicit numeric zero is a measured value. A missing field is unknown.

Codex cumulative counters are used only to check the increments. In a fork, the
check includes the validated ancestor increments. The reported spend includes
only the primary session's calls. Replayed ancestor timestamps do not turn old
calls into new spend. Supply the original session separately if you want its
calls too. Identical full copies can be deduplicated; conflicting copies or
conflicting labels are refused. File aliases are refused before accounting.

Each metric has `value`, `measured_subtotal`, `covered_calls`, `missing_calls`,
`unavailable_sources` and `status`. If a source is missing, its call count is
unknown. It is not added to `missing_calls` as zero. The main total becomes null;
the known subtotal stays visible. Missing optional thinking or model metadata
alone does not fail otherwise complete volume.

The report covers the supplied files and recognized native record shapes. It
cannot find an omitted session or prove that an export contains every call.
Codex needs a complete, matching final primary-thread counter. A lost valid tail
that also loses its final counter can be undetectable. Unknown accounting shapes,
malformed JSON, duplicate JSON keys, non-finite numbers, torn lines and conflicting
counters are refused. Unsupported usage token names and nested locations are
refused too. The two observed ephemeral cache breakdowns remain valid at their
root and iteration cache locations. They are not added to the total.
Inputs must be regular files and stay stable during reading. If an aggregate
cannot be serialized to JSON, the command returns `INTERNAL_FAILURE` with code 4
and keeps raw values out of the error.

Available native model and effort fields are retained with their source. A Codex
`turn_context` is matched by turn ID and must precede the first record of the
call. A later duplicate cannot fill missing model or effort data. It is context
metadata, not independent proof of the served model. Session-start CLI versions
are separate from actual per-call versions. Missing values stay null. Groups
retain the caller's labels and these available execution fields.

Cost, subscription quota weights, actual call latency, owner-blocked time, and
quality remain `UNAVAILABLE`. Token volume is not a price or quota measurement.
The tool does not apply one cache-price schedule to every model.

## Limits and result codes

| reader budget | default | behavior |
|---|---:|---|
| one record, including its newline | 16,777,216 bytes | `--max-record-bytes N` changes it |
| retained unique call identities across the inputs, ancestors included | 100,000 | `--max-calls N` changes it |
| each source's context and session-metadata identity maps | the call budget, separately for each map | refuses excess identities |
| retained metadata value or identity | 512 Unicode code points | refuses excess text; never truncates it |

Raw call IDs are hashed and discarded within the record budget. A call ID in the
report is one full SHA256 of UTF-8
`json.dumps([format, logical_session, native_call_id], ensure_ascii=False, separators=(",", ":"))`.
The source digest is SHA256 of the original file bytes. Hashes are evidence
references. They do not authenticate an owner or isolate a process.

The limits bound this reader. They are not new review, token, gate, or owner-decision
rules. A limit refusal is not a partial success. Call references keep the first
and last line and a row count, rather than a list that grows for every duplicate.
The original source remains the full evidence.

| exit | result |
|---:|---|
| 0 | complete volume for the selected calls, or help |
| 2 | invalid command, time range, TOML or manifest schema |
| 3 | incomplete evidence, unsupported input, resource limit or a changing source |
| 4 | I/O or internal failure |
| 5 | malformed or conflicting source data; failed counter reconciliation |

All use `dflow.result/1`. A successful or partial report in `items[0]` uses
`dflow.telemetry/1`. A refusal gives a fixed reason and location without echoing
source text or an exception body. TOML syntax lines are available on Python
3.15.2. They stay unknown on the tested Python 3.12.3. Semantic field checks name
the field or table index; no custom TOML parser invents a line number.

## Findings from this study

The following are [Confirmed] only for the retained snapshots checked on
2026-10-29. These are small local checks, not reconciliation of the proposal's
October archive figures. Matching a final thread counter alone does not prove
that replayed calls are new spend in those dates. The full archive needs a
fork/replay audit before it is used as an efficiency baseline.

| saved sample | primary calls | primary raw tokens |
|---|---:|---:|
| Claude, October 7 | 33 | 5,337,650 |
| Codex, October 14 | 17 | 1,278,928 |
| Codex fork/compaction, October 28 | 180 | 32,313,194 |

The fork snapshot has 5,644 increments including its ancestors. Their raw sum is
1,224,961,721 and matches the final primary-thread counter. This is a different
quantity from the primary session's spend. The old event counter differs from
that thread counter. It is not a substitute for incremental usage.

[Confirmed, this VM] A native Agent canary preserved the exact prompt bytes in
its tool input, returned prompt, and child transcript. Its child model and high
effort were visible. A real review attempt also showed why `status: completed`
is insufficient: its body contained a quota error and only a partial answer.
That attempt was not counted as a valid review.

[Open] Parent restart, all cancellation/error/timeout paths, durable hooks, and
the full native completion matrix remain unproved. The study has an individual
V1–V14 evidence/gap map. It does not claim that an attach adapter is ready.

[Confirmed, this VM] Two small `systemd --user` probes worked: a silent job kept
running after its caller left, and a deadline stopped a detached child in the
job's control group. Lingering was already enabled. The full supervisor contract
and the second machine are still [Open]. No supervisor was added to this package.

[Confirmed, this VM] The read-only GitLab version response was 19.5.1 with
`enterprise: false`. License access, effective protected-action permissions,
CI credentials, and runner reach are [Open]. No identity or permission setting
was changed. Credential checks used names and file metadata, not secret values.

The supplied archive baseline, a ten-slice quality baseline, the defect corpus,
and the second-machine comparisons remain `UNAVAILABLE`. They are not successful
replays. No model-call, token, price or elapsed-time saving is claimed from this
pilot.

## Items left unchanged in the proposal

These points need care before any later engine is built. The supplied revision 5
text and the canonical flow rules were not rewritten for this pilot.

- Existing authorization must carry forward. The future ledger must not add a
  fresh chat stop for work that the owner has already authorized. Its exact-scope,
  expiry and single-use rules need an explicit mapping to current delegation.
- Current `dmf` allows reviewed fixes between rounds. A guard cannot demand that
  every historical plan, test and change round name one final source identity.
  It must check the right artifact and revision for each stage.
- A valid quota fallback fills a reviewer seat. Missing seats are reported
  separately. The author's-family sentence in portable `REVIEWING.md` is an
  example of a profile, not a universal extra seat. Missing served-effort proof
  stays a disclosed limit under current rules; a stronger gate needs a decision.
- A hash chain alone cannot detect every lost valid suffix without a retained
  tip. A surviving later snapshot can detect some such loss. Durable commit and
  receipt of a reply are separate facts; recovery cannot infer both from a line.
- Native or relayed owner records are not owner authentication when the agent
  can edit the source. The proposal is right to keep the security track separate.
- The offline command has no automatic file sink or XDG state tree. This is a
  deliberate phase-0 cut from section 5, not a full execution-layer contract.
- Required raw evidence stays private. Disposable task builds and caches follow
  the existing safe-cleanup rule. No new evidence-pruning period is adopted.

## Checks, evidence and next work

Run the suite with the declared interpreter:

```sh
python3.15 -B -m unittest discover -s tests -v
```

Tests cover arithmetic, split/overlap/fork identity, missing fields, time windows,
metadata, resource boundaries, real file changes, one-line CLI results and privacy.
The memory witness fixes record size and call count, grows ignored input from
1,000 to 10,000 one-KiB rows, and allows at most two MiB of extra traced allocation.
Wrong-code checks include buffering the input, counting ancestors as new spend,
using only total counters, and resetting the call budget for each file.

The retained working plan/report on the implementation machine is
`/home/toha/.claude-review-evidence/dflow-phase0-20261029/PLAN.md`.
It indexes exact source identities, full reviews, decisions, red and green test
runs, native sample receipts, `spike/REPORT.json`, `spike/VALIDITY.md`, measurements,
delivery, rollback, and cleanup. Frozen earlier plans remain beside it. Native
logs are private and are not part of this repository. Follow that report's restore
steps if a retained large input has been compressed.

Full phase-0 acceptance is still open. Next evidence is the original archive
scope, the quality corpus, the other machine and the missing native invocation
signals. Phase 1 also needs its scope approval, source-equivalent archive replays,
and live shadow/opt-in checks. Phase 2, identity separation, sandbox adoption,
new sessions, parallel gates and instruction packs keep their separate decisions.
Rollback of this optional command is a focused source revert. It has no service,
database or state migration to reverse.
