# Token-Efficient AI Agent System

## 1. Goal

Build a generic system that reduces token consumption, monetary cost, and quota failures for AI-agent work while preserving the agent's ability to inspect all information it needs.

The system must work with:

* coding agents;
* review agents;
* research agents;
* DevOps agents;
* documentation agents;
* test agents;
* multiple model vendors;
* CLI agents;
* API-based agents;
* local/self-hosted agents where possible.

The main rule is:

> **Reduce repeated information, not available information.**

The agent must still be able to access the complete repository, complete evidence, complete logs, and complete documents when needed.

The optimization layer controls what is automatically injected into context.

It must not silently hide information.

---

# 2. Optimize three different resources

Do not treat these as one thing.

## 2.1 Token volume

```text
total_tokens =
    input_tokens
  + output_tokens
```

Goal:

```text
token_saving =
    1 - optimized_total_tokens / baseline_total_tokens
```

---

## 2.2 Monetary cost

Different token types can have different prices.

Track separately:

```text
fresh_input_tokens
cached_input_tokens
cache_write_tokens
output_tokens
```

Calculate using the real provider prices:

```text
cost =
    fresh_input_tokens  * input_rate
  + cached_input_tokens * cached_rate
  + cache_write_tokens  * cache_write_rate
  + output_tokens       * output_rate
```

Goal:

```text
cost_saving =
    1 - optimized_cost / baseline_cost
```

Token saving and cost saving are not necessarily equal.

---

## 2.3 Availability

A cheap system is useless if agents regularly die because of:

* exhausted credits;
* rate limits;
* context limits;
* provider quota;
* authentication failures;
* unavailable models.

Track:

```text
completion_rate
incomplete_rate
quota_failures
rate_limit_failures
```

Optimize this separately.

---

# 3. High-level architecture

Use five context layers.

```text
┌──────────────────────────────────────────┐
│ L0 — SYSTEM KERNEL                       │
│ tiny, stable, always loaded              │
└────────────────────┬─────────────────────┘
                     │
┌────────────────────▼─────────────────────┐
│ L1 — PROJECT MEMORY                      │
│ compact project facts                    │
└────────────────────┬─────────────────────┘
                     │
┌────────────────────▼─────────────────────┐
│ L2 — TASK CAPSULE                        │
│ stable for current task                  │
└────────────────────┬─────────────────────┘
                     │
┌────────────────────▼─────────────────────┐
│ L3 — CURRENT DELTA                       │
│ only what changed since last phase       │
└────────────────────┬─────────────────────┘
                     │
┌────────────────────▼─────────────────────┐
│ L4 — FULL EVIDENCE STORE                 │
│ repository, files, logs, prior results   │
│ available on demand, not always injected │
└──────────────────────────────────────────┘
```

This is the central design.

Do not continuously send the whole history back to the model.

---

# 4. Layer 0 — System Kernel

Create a very small machine-wide instruction file.

Example:

```text
/etc/ai-agent/KERNEL.md
```

or equivalent for the operating system.

Target size:

```text
~1,000–2,000 tokens
```

It should contain only rules that must apply to every task.

For example:

```text
- Work only from verified current state.
- Full evidence remains accessible.
- Do not invent missing information.
- Avoid rereading unchanged information.
- Large outputs must be stored as artifacts.
- Put only useful excerpts into model context.
- Never destroy full evidence when compacting context.
- Record token/cost telemetry.
- A failed/incomplete agent run is never a successful run.
- Use fresh sessions at meaningful phase boundaries.
```

Do not put long explanations in this file.

Keep detailed documentation separately.

---

# 5. Layer 1 — Project Memory

Each project gets a compact machine-readable memory.

For example:

```text
.ai/project-memory.yaml
```

Example:

```yaml
project:
  name: payments-api
  repository: /srv/payments-api
  revision: git
  primary_language: go

structure:
  app: cmd/api
  internal: internal/
  tests: tests/
  deploy: deploy/

commands:
  test: go test ./...
  race: go test -race ./...
  lint: golangci-lint run
  build: go build ./cmd/api

important_files:
  - go.mod
  - go.sum
  - README.md
  - .golangci.yml

deployment:
  type: kubernetes
  manifests: deploy/
```

This prevents every new session from rediscovering the project from dozens of files.

But it must never become stale silently.

Store:

```yaml
memory_metadata:
  generated_at: ...
  source_revision: ...
  content_hash: ...
```

If the repository materially changes, update it.

---

# 6. Layer 2 — Task Capsule

At the beginning of every task create a compact task document.

Example:

```text
.ai/tasks/<task-id>/task.yaml
```

Example:

```yaml
task_id: auth-timeout-20260912

problem:
  summary: Requests occasionally bypass authentication after timeout.

baseline:
  commit: 8ac4912

scope:
  - internal/auth/
  - cmd/api/

acceptance:
  - timed-out authentication never fails open
  - existing successful authentication unchanged

non_goals:
  - redesign authentication architecture
  - change token format

important_paths:
  - internal/auth/middleware.go
  - internal/auth/session.go

evidence_root:
  .ai/tasks/auth-timeout-20260912/evidence/
```

This capsule stays mostly identical throughout the task.

It is an ideal prompt-cache candidate.

---

# 7. Layer 3 — Delta State

Never carry the complete conversation from one phase or review round to another.

Create a small current-state file.

Example:

```text
.ai/tasks/<id>/delta.yaml
```

Example:

```yaml
phase: review-2

changed_since_previous:
  - internal/auth/middleware.go:88-112
  - tests/auth_timeout_test.go

resolved:
  - F01: fixed incorrect timeout fallback
  - F02: rejected; contradicted by upstream API contract

open:
  - F03: verify concurrent timeout path

new_evidence:
  - evidence/test-race.txt
  - evidence/timeout-reproduction.txt
```

A new agent receives:

```text
kernel
+
project memory
+
task capsule
+
current delta
```

Not the complete previous conversation.

---

# 8. Layer 4 — Evidence Store

All complete information stays outside model context.

Example:

```text
.ai/
  tasks/
    <task-id>/
      evidence/
      reviews/
      logs/
      raw/
```

Store:

```text
full command output
test output
compiler output
review responses
full diffs
API responses
research documents
benchmark results
```

Every artifact should have:

```text
path
timestamp
hash
producer
command/source
```

For example:

```yaml
artifact:
  path: evidence/tests-full.txt
  sha256: ...
  created_at: ...
  command: go test ./...
  exit_code: 0
```

The model may receive:

```text
Tests passed.

Full evidence:
.ai/tasks/X/evidence/tests-full.txt

SHA-256:
...
```

instead of 20,000 lines of passing test output.

---

# 9. Fresh-session architecture

A major saving comes from avoiding endlessly growing conversations.

Use fresh sessions at meaningful boundaries.

Example:

```text
DISCOVERY
    ↓ handoff
PLANNING
    ↓ handoff
IMPLEMENTATION
    ↓ handoff
VALIDATION
    ↓ handoff
REVIEW
```

Each new session receives compact state, not conversation history.

A handoff should contain:

```yaml
phase_completed:
baseline:
current_revision:
work_completed:
important_decisions:
open_items:
evidence_paths:
next_action:
```

The handoff should normally be hundreds of tokens, not tens of thousands.

---

# 10. Read-on-demand instead of preload-everything

Agents must retain access to everything.

But do not preload everything.

Bad:

```text
Here are 42 project files.
Here are 9 previous reviews.
Here are 30,000 lines of logs.
Now inspect one function.
```

Better:

```text
Repository: /srv/project

Relevant starting paths:
- internal/foo.go
- internal/bar.go

Complete repository remains available.
Inspect additional files when evidence requires it.
```

This preserves visibility while reducing automatic context.

---

# 11. File-read discipline

Track file reads inside each agent session.

Maintain approximately:

```text
path
content_hash
last_read_time
ranges_read
```

Before rereading:

```pseudo
current_hash = hash(file)

if current_hash == previously_read_hash:
    if requested_range already available:
        reuse existing context
    else:
        read only required range
else:
    reread changed part or full file if necessary
```

Do not implement:

```text
never reread a file
```

That is unsafe.

Implement:

> Do not repeatedly read unchanged content without a reason.

Prefer:

```text
symbol read
specific line range
git diff
changed hunk
```

over:

```text
cat entire-file
```

---

# 12. Large tool-output handling

Never inject large raw outputs directly unless necessary.

Use this pipeline:

```text
tool execution
      │
      ▼
write full raw artifact
      │
      ▼
calculate hash
      │
      ▼
deterministic reduction
      │
      ▼
small useful result -> model
```

For example:

```text
go test ./...
```

produces 15,000 lines.

Store:

```text
evidence/go-test-full.txt
```

Context might receive:

```text
Command: go test ./...
Exit: 1

3 failing tests:

1. TestAuthTimeout
   auth_test.go:144
   expected deny, got allow

2. TestConcurrentTimeout
   ...

Full output:
evidence/go-test-full.txt
```

---

# 13. Deterministic compression first

Before using another LLM to summarize output, apply normal software transformations.

Examples:

```text
remove ANSI escape codes
remove progress bars
collapse identical repeated lines
collapse repeated stack frames
extract ERROR/WARN/FAIL
extract failed tests
extract command/version/exit code
extract changed files
```

Only use model summarization when deterministic processing is insufficient.

Why?

Because using an LLM to save LLM tokens can consume a large part of the saving.

---

# 14. Compression accounting

Measure the complete optimization cost.

Track:

```text
raw_output_tokens
tokens_injected_after_compaction
summarizer_input_tokens
summarizer_output_tokens
rehydration_tokens
```

Calculate:

```text
net_saving =
baseline_context_tokens
-
(
 optimized_context_tokens
 + summarization_tokens
 + rehydration_tokens
)
```

Never claim savings using only the final shortened prompt.

---

# 15. Prompt-cache architecture

For providers supporting prompt caching, order context from most stable to most variable.

```text
[1] machine kernel
[2] project rules
[3] task capsule
[4] current delta
[5] current question
```

Do not put volatile information before stable information if that breaks provider caching.

Stable sections should remain byte-identical where practical.

Measure:

```text
cache_write_tokens
cache_read_tokens
cache_hit_ratio
cache_write_cost
cache_read_cost
```

Do not assume caching is beneficial.

A cache that repeatedly expires before reuse can cost more than no cache.

---

# 16. Reviewer architecture

Review is different from implementation.

Do not impose aggressive context caps on review agents.

Each independent reviewer must have:

```text
full repository access
full evidence access
task capsule
current delta
important previous dispositions
```

But it does not need full previous reviewer conversations.

Review session:

```text
stable context
    +
task capsule
    +
delta
    +
compact disposition ledger
    +
paths to complete evidence
```

---

# 17. Disposition ledger

Instead of passing pages of discussion between review rounds, use a compact ledger.

Example:

```text
ID | location | status | evidence
F01 | auth.go:88 | ACCEPT | test T12
F02 | cache.go:44 | REJECT | API spec §3.2
F03 | worker.go:91 | OPEN | needs concurrency test
```

Closed findings remain reopenable.

A reviewer may say:

```text
Reopen F02 because new evidence X contradicts the old disposition.
```

This preserves reasoning without preserving all prose.

---

# 18. Reviewer evidence-access telemetry

Every reviewer should report what it actually inspected.

Example:

```yaml
evidence_accessed:
  files:
    - internal/auth/middleware.go
    - internal/auth/session.go
  artifacts:
    - evidence/race-test.txt
  commands:
    - go test ./internal/auth/...
```

This does not require it to inspect every available file.

It tells you whether the reviewer really investigated or only answered from the brief.

---

# 19. Independent review

If multiple reviewers are used:

```text
Reviewer A ─┐
Reviewer B ─┼── same frozen artifact
Reviewer C ─┘
```

They should not see each other's outputs during the same round.

This keeps reviews independent.

Use separate output files:

```text
reviews/round-1/family-a.md
reviews/round-1/family-b.md
reviews/round-1/family-c.md
```

Never use one shared writable file.

---

# 20. Do not use cascades for negative assurance

A model cascade can work well for tasks such as:

```text
classification
extraction
format transformation
simple generation with deterministic tests
```

Example:

```text
cheap model
   ↓ if uncertain
expensive model
```

But do not use this automatically for tasks whose output is:

```text
"I found no security defect."
```

A cheap model may confidently miss the defect.

You cannot easily score confidence in an absence.

Therefore, review/security/negative-assurance tasks should normally keep the intended reviewer quality.

---

# 21. Model routing

For normal agent work, model routing can save large amounts of cost.

Example categories:

```text
low-cost model:
- classify logs
- extract errors
- summarize deterministic output
- generate metadata
- simple file transformations

strong model:
- architecture
- difficult debugging
- security review
- final code review
- ambiguous research
```

Routing must be explicit and measurable.

Do not silently downgrade important review agents.

---

# 22. Output discipline

Output can be expensive.

Agents should produce exactly the useful result.

Implementation agents usually do not need to repeatedly explain:

```text
what they are about to do
what they just did
a full recap after every operation
```

Prefer structured concise responses.

However:

**Do not truncate required review evidence.**

The reviewer's findings and supporting evidence are part of the product.

---

# 23. Availability preflight

Before expensive runs, check provider health and entitlement.

Example:

```pseudo
for reviewer in reviewers:
    check auth
    check model availability
    check account/quota status if API exposes it
    check required permissions
```

Record:

```text
READY
QUOTA_LOW
QUOTA_UNKNOWN
AUTH_FAILED
MODEL_UNAVAILABLE
RATE_BLOCKED
```

Never invent quota information if the provider does not expose it.

---

# 24. Historical reserve model

After sufficient data exists, calculate resource requirements.

For each:

```text
provider
model
reasoning level
task type
```

calculate:

```text
p50 tokens
p90 tokens
p95 tokens
p99 tokens
```

Then optionally require:

```text
starting_available_quota >= p95 * safety_factor
```

Example:

```text
safety_factor = 1.2
```

Do not derive this from one run.

---

# 25. Normal budget warnings

A budget should normally warn, not terminate.

Example:

```text
WARN_INPUT_TOKENS=400000
WARN_TOTAL_TASK_TOKENS=2000000
```

Behavior:

```text
threshold exceeded
       ↓
allow current operation to finish
       ↓
mark BUDGET_EXCEEDED
       ↓
do not automatically start another expensive phase
```

A warning is an operational signal.

It is not a correctness result.

---

# 26. Catastrophic runaway fuse

A separate emergency limit protects against broken loops.

Example later, after collecting enough data:

```text
catastrophic_limit =
    historical_p99 * 2
```

If triggered:

```text
terminate operation
mark INVALID / INCOMPLETE
preserve logs
never call it PASS
```

Do not confuse this with the normal budget.

---

# 27. Telemetry data model

Create one record per AI execution.

Example:

```json
{
  "timestamp": "...",
  "project": "payments-api",
  "task_id": "auth-timeout",
  "phase": "review",
  "round": 2,

  "provider": "...",
  "family": "...",
  "model": "...",
  "reasoning_effort": "...",
  "agent_version": "...",

  "stable_prefix_tokens": 12000,
  "task_capsule_tokens": 3000,
  "delta_tokens": 1500,

  "fresh_input_tokens": 40000,
  "cached_input_tokens": 80000,
  "output_tokens": 9000,

  "tool_calls": 22,
  "file_reads": 14,
  "repeated_unchanged_reads": 2,

  "cost_usd": 1.44,

  "duration_seconds": 220,

  "status": "valid",
  "verdict": "changes_requested",
  "findings": 3
}
```

Use JSONL, SQLite, PostgreSQL, ClickHouse, Prometheus, or another suitable system.

Start simple.

JSONL or SQLite is enough initially.

---

# 28. Separate token-origin telemetry

Where possible distinguish:

```text
system/kernel tokens
project-memory tokens
task-capsule tokens
delta tokens
user-message tokens
tool-result tokens
repository-read tokens
assistant-output tokens
```

This is extremely important.

Without attribution you only know:

```text
we consumed 1,000,000 tokens
```

With attribution you might learn:

```text
420k repository investigation
300k repeated history
180k tool output
70k system rules
30k final response
```

Now you know what is safe to optimize.

---

# 29. Baseline fingerprint

Every measurement must identify the environment that produced it.

Record:

```text
model
provider
reasoning effort
agent version
tool versions
tool schema version if available
instruction/kernel hash
project-rule hash
cache settings
context-compaction settings
```

If one materially changes, do not blindly compare it to the old baseline.

---

# 30. Quality benchmark

Never evaluate optimization only by token reduction.

Build a benchmark containing known problems.

For coding/review systems use:

```text
historical real bugs
mutants
known security defects
known bad implementations
known-good changes
```

Example:

```yaml
cases:
  - id: D001
    severity: critical
    description: authentication fail-open
    expected_detection: true

  - id: D002
    severity: high
    description: race in shared state
    expected_detection: true
```

Run both:

```text
baseline configuration
optimized configuration
```

against the same benchmark.

---

# 31. Quality metrics

Track:

```text
critical_defect_recall
overall_defect_recall
false_positive_rate
completion_rate
incomplete_rate
```

Example:

```text
critical defects: 10
detected: 10

critical recall = 100%
```

Do not use:

```text
number of findings
```

alone as quality.

One reviewer may report 20 weak findings.

Another may report 8 real defects.

The second reviewer can be better.

---

# 32. Compare shared-success and all-attempted sets

Report two views.

## Shared-success

Tasks both configurations completed successfully.

Useful for efficiency comparison.

## All attempted

Every attempted task.

This captures regressions where optimization causes more failures.

Example:

```text
Baseline:
98/100 completed

Optimized:
72/100 completed
```

The optimized system must not claim victory just because its 72 successful cases were cheaper.

---

# 33. Main metrics

At minimum report:

```text
tokens per completed task
tokens per successful review
cost per completed task
cost per successful review
p50 tokens
p90 tokens
p95 tokens
completion rate
critical-defect recall
overall-defect recall
```

For quota-limited environments also track:

```text
quota consumption per successful task
```

---

# 34. Statistics

AI-agent token use can vary heavily between runs.

Do not trust one test.

For benchmarks run repeated trials where practical.

Report:

```text
median
p90
p95
```

Avoid relying only on mean.

For important comparisons run:

```text
same task
same baseline
same model
several independent repetitions
```

---

# 35. Feature flags

Every optimization must be independently disableable.

Example:

```yaml
token_economy:

  enabled: true

  fresh_sessions: true

  compact_handoffs: true

  compact_review_briefs: true

  project_memory: true

  tool_output_compaction: true

  avoid_redundant_reads: true

  prompt_cache_optimization: true

  quota_preflight: true

  model_routing: false

  catastrophic_fuse: true
```

This is extremely important.

If quality drops, you must be able to return immediately to baseline behavior.

---

# 36. Full fallback mode

Support:

```yaml
token_economy:
  enabled: false
```

This should restore the original behavior without changing agent source code.

Never build optimization so deeply into the system that disabling it requires rewriting prompts or programs.

---

# 37. Recommended filesystem layout

Example:

```text
/etc/ai-agent/
  KERNEL.md
  token-economy.yaml

~/.ai-agent/
  providers.yaml
  telemetry.jsonl

PROJECT/
  .ai/
    project-memory.yaml

    tasks/
      TASK-ID/
        task.yaml
        delta.yaml
        handoff.yaml

        evidence/
          raw/
          compact/

        reviews/
          round-1/
          round-2/

        metrics/
          runs.jsonl
```

---

# 38. Recommended implementation components

Build these small components rather than one large framework.

## A. Context Builder

Produces:

```text
kernel
+
project memory
+
task capsule
+
delta
```

---

## B. Artifact Store

Stores complete logs/evidence.

Functions:

```text
put()
get()
hash()
metadata()
```

---

## C. Output Compactor

Processes large command/tool output.

---

## D. Read Tracker

Tracks:

```text
file
hash
ranges
read count
```

---

## E. Telemetry Collector

Normalizes provider usage data.

---

## F. Cost Calculator

Loads provider pricing/config and calculates actual cost.

---

## G. Quota Preflight

Checks provider/account state where possible.

---

## H. Benchmark Runner

Runs baseline vs optimized configurations.

---

## I. Feature-Flag Controller

Turns each optimization on/off independently.

---

# 39. Suggested internal interfaces

Example pseudo-code:

```go
type Usage struct {
    FreshInputTokens  int64
    CachedInputTokens int64
    CacheWriteTokens  int64
    OutputTokens      int64
}

type RunResult struct {
    Status       string
    Usage        Usage
    Cost         float64
    ToolCalls    int
    FileReads    int
    Findings     []Finding
    Evidence     []Artifact
}
```

Context:

```go
type ContextPackage struct {
    Kernel        []byte
    ProjectMemory []byte
    TaskCapsule   []byte
    Delta         []byte
}
```

Artifacts:

```go
type Artifact struct {
    Path      string
    SHA256    string
    CreatedAt time.Time
    Source    string
}
```

---

# 40. Implementation phases

Do not build everything at once.

## Phase 1 — Observe only

Build telemetry first.

Change no agent behavior.

Collect:

```text
input
output
cached
cost
tools
file reads
completion
```

This creates the real baseline.

---

## Phase 2 — Fresh sessions

Introduce:

```text
task capsule
handoff
delta
```

Stop carrying complete conversation history.

Measure again.

---

## Phase 3 — Tool-output compaction

Store complete artifacts.

Inject compact representations.

Measure again.

---

## Phase 4 — Read deduplication

Prevent redundant unchanged full-file reads.

Measure again.

---

## Phase 5 — Cache optimization

Reorder stable prefixes.

Measure actual cache effectiveness.

---

## Phase 6 — Compact machine kernel

Reduce permanently injected instructions.

Keep full documentation accessible.

Measure again.

---

## Phase 7 — Availability controls

Add:

```text
quota preflight
provider health
historical reserve calculation
runaway protection
```

---

## Phase 8 — Model routing

Only after good metrics exist.

Route cheap, verifiable tasks to cheaper models.

Do not initially apply this to high-risk review.

---

# 41. Experimental method

Change one optimization at a time.

Bad:

```text
enable compact prompts
enable new model
enable caching
change agent version
change review strategy

compare result
```

You will not know what caused the saving.

Better:

```text
Baseline
    ↓
Fresh sessions
    ↓ measure
Tool compaction
    ↓ measure
Read deduplication
    ↓ measure
Cache optimization
    ↓ measure
Kernel reduction
    ↓ measure
```

---

# 42. Acceptance criteria

An optimization can be accepted only when:

```text
token usage decreases materially
OR cost decreases materially
OR completion availability improves
```

AND:

```text
critical quality does not regress
```

Specifically:

```text
critical defect recall does not fall
completion rate does not materially fall
incomplete rate does not materially rise
full evidence remains accessible
review visibility remains unchanged
```

---

# 43. Do not prematurely choose a universal saving threshold

At the beginning do not hard-code:

```text
must save 20%
```

First measure several real tasks.

Then decide what makes the added complexity worthwhile.

For example, later:

```yaml
acceptance:
  minimum_token_saving_percent: 15
  minimum_cost_saving_percent: 15
  maximum_completion_regression_percent: 0
  critical_defect_recall_percent: 100
```

Those numbers are business decisions, not universal scientific constants.

---

# 44. Dashboard

Eventually expose:

```text
Today
---------------------------------
Tasks                    34
Successful               32
Incomplete                2

Input tokens          8.2M
Cached tokens         5.4M
Output tokens         0.9M

Cost                  €XX
Estimated baseline    €YY
Saving                ZZ%

Repeated reads          81
Avoided reads          214

Cache hit ratio        68%

Reviews completed       11
Critical recall       100%
```

Break down by:

```text
provider
model
project
task type
phase
agent
```

---

# 45. Important anti-patterns

Do not optimize this way:

### Hard context cap everywhere

Can silently prevent a reviewer from investigating enough.

### Delete old evidence

Wrong. Store it outside context instead.

### Summarize everything with another LLM

Can consume much of the saving.

### Cheap-model cascade for every task

Unsafe when success means finding an unknown defect.

### Count cache hits as token reduction

Caching usually changes economic processing, not the amount of context logically consumed.

### Measure only successful runs

Hides expensive failures.

### Measure only average tokens

AI runs are highly variable.

### Prevent every reread

Files change and exact verification sometimes requires rereading.

### Optimize before collecting telemetry

Then you cannot know whether anything improved.

---

# 46. Core algorithm

Conceptually every agent request should behave like this:

```text
1. Identify task and phase.

2. Load small stable kernel.

3. Load project memory.

4. Load current task capsule.

5. Load current delta.

6. Do NOT load full old conversation.

7. Give agent complete access to repository/evidence.

8. Agent reads additional information only when needed.

9. Track reads and tool calls.

10. Store large outputs externally.

11. Inject only useful compact output.

12. Collect provider token/cache/cost telemetry.

13. Write compact handoff at phase end.

14. Start next phase in fresh context.

15. Compare cost/quality against baseline.
```

That is the complete system in one algorithm.

---

# 47. The most important design boundary

The system should distinguish:

```text
INFORMATION AVAILABLE TO THE AGENT
```

from:

```text
INFORMATION AUTOMATICALLY PRESENT
IN EVERY MODEL REQUEST
```

The first should remain broad.

The second should be aggressively controlled.

That difference is where most safe savings come from.

---

# 48. Final target architecture

```text
                     ┌─────────────────┐
                     │   AI REQUEST    │
                     └────────┬────────┘
                              │
                     ┌────────▼────────┐
                     │ Context Builder │
                     └────────┬────────┘
                              │
          ┌───────────────────┼────────────────────┐
          │                   │                    │
    ┌─────▼─────┐       ┌─────▼──────┐      ┌─────▼─────┐
    │  Kernel   │       │Task/Project│      │   Delta   │
    └───────────┘       └────────────┘      └───────────┘
                              │
                     ┌────────▼────────┐
                     │      Agent      │
                     └───┬─────────┬───┘
                         │         │
                  file/tool      model output
                         │         │
              ┌──────────▼──┐     │
              │Artifact Store│     │
              └──────┬──────┘     │
                     │            │
             ┌───────▼───────┐    │
             │   Compactor   │────┘
             └───────────────┘

                         │
                         ▼
                ┌─────────────────┐
                │    Telemetry    │
                │ tokens          │
                │ cost            │
                │ cache           │
                │ availability    │
                │ quality         │
                └─────────────────┘
```

# 49. Final principle

The system must never optimize by making the AI artificially blind.

It should optimize by eliminating:

* repeated conversation history;
* repeated instructions;
* repeated unchanged file contents;
* useless tool output;
* duplicated evidence;
* unnecessary prose;
* failed launches that could have been detected beforehand;
* cache-hostile prompt structure.

Keep:

* full repository access;
* full evidence;
* strong reviewers;
* necessary reasoning;
* exact verification.

In one sentence:

> **Store everything, expose everything, automatically inject only what is needed now.**
