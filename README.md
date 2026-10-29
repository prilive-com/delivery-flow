# delivery-flow

A mandatory 12-step delivery flow for AI-assisted software work, with `dmf` as the default and `dsf` for simpler work,
independent reviewer rules, and token-budget rules that cut repetition while keeping full access.

| file | what it is |
|---|---|
| `DELIVERY-FLOW.md` | the flow: twelve steps, what each requires, and what counts as DONE |
| `REVIEWING.md` | how to run the reviewer legs steps 4 and 11 require |
| `TOKEN-BUDGET.md` | measured review costs, corrections, and rules for cutting waste without cutting the review |
| `TOOLING.md` | documentation and browser tools, optional complexity/duplication trials, reviewer capabilities, and what is lost without them |
| `token-economy-common.md` | a generic design for context, evidence storage, telemetry, and token, cost and quota control |
| `README.md` | this map and the adoption notes |
| `docs/DFLOW-PILOT.md` | read-only token telemetry, study findings, limits and next steps |
| `docs/DFLOW-INTEGRATION.md` | active workflow discovery, native execution/waits, measurement and installation checks |
| `dflow/` | the standard-library Python telemetry command |
| `tests/` | synthetic tests for the telemetry reader |
| `.python-version` | the telemetry tool's declared Python 3.15.2 interpreter |

In `DELIVERY-FLOW.md`, **I** and **me** are the person who adopts the flow; **you** is the agent
working for them.

## Current state (2026-10-29)

The delivery rules are in use. The repository also has an optional `dflow`
telemetry tool, delivered in [PR #21](https://github.com/prilive-com/delivery-flow/pull/21).
The tool reads saved logs. The active flow now discovers the installed tooling,
reuses retained artifacts and native completion waits, and measures supported
completed scopes. [The integration guide](docs/DFLOW-INTEGRATION.md) gives the
procedure. Agents keep all existing planning, review, gate and delivery rules.

| part | current state |
|---|---|
| Delivery flow | Active. `dmf` is the default, with two required rounds and up to three per stage. `dsf` has two final rounds. See [the mode table](#flow-modes-dmf-is-the-default). |
| Reviewer policy | The maintainer prefers Claude, then Codex, with quota fallbacks. Each adopter defines a local profile. See [the policy below](#maintainers-current-reviewer-policy). |
| Active execution and measurement procedure | In the flow rules. Discover installed tooling, reuse artifacts, wait natively and measure supported completed scopes. Missing measurement is recorded without a new owner stop. Install and verify actual shared instruction copies as well as publishing the source. |
| `dflow telemetry` | Delivered and read-only. The active procedure uses supported saved logs when available. See [the pilot guide](docs/DFLOW-PILOT.md). |
| Full phase-0 acceptance | Open. The full archive baseline, quality corpus, second-machine checks and missing native Agent completion evidence are still needed. |
| Native Agent review adapter | Study only. Completion, cancellation and parent-restart gaps remain. |
| Execution engine, phases 1 and 2 | Deferred. The state store, workflow guards, job supervision, gate/review runners and owner ledger are not part of the delivered tool. |
| Later rollout decisions | Identity separation, sandbox adoption, new sessions, parallel gates and instruction packs keep their separate decisions and evidence requirements. |

The pilot has not proved a reduction in model calls, tokens, cost or end-to-end
time. [The study and next steps](docs/DFLOW-PILOT.md#checks-evidence-and-next-work)
explain its limits. `token-economy-common.md` remains a design document.

## Using it

Point your agent's always-loaded instruction file at `DELIVERY-FLOW.md` — copy it, symlink it, or
import it, whichever your tool supports. Keep it as the canonical copy and edit it there; if your
tool needs the text inlined, generate that copy rather than editing it, and check the two still
match.

Load `REVIEWING.md` and `TOKEN-BUDGET.md` through that same instruction file. Use `TOOLING.md` as
the capability reference; step 1 records what is actually available on your machine. It names
Context7 for documentation discovery and Playwright for browser proof. Discovery alone leaves a
claim INFERRED; a version-exact source is needed for VERIFIED. Another real browser driver can
supply browser proof; a component test cannot.

**Then write a complete local reviewer-tooling profile**: the actual families and seats, tools,
paths, tiers, invocation and failure handling on your machine. This repository gives the
maintainer's current policy as an example below; it does not contain that machine's full profile. Record invocations, validity checks and availability probes. Name its path in the
project's instruction file and load it the same way. Keep it local — accounts and quotas belong
to your machine. `TOOLING.md` is the reference, never that profile.

The flow decides **whether** a step is required and **what counts as done**. Your project decides
**how it is spelled** — commands, paths, gates, integration branch. Where they conflict on a command
or a path, the project wins. Where the project would remove a step, the flow wins and the conflict
is a stop.

## Maintainer's current reviewer policy

This is the maintainer's current machine policy, not a vendor requirement of the portable flow.
An adopter sets their own policy in the local profile. The maintainer's preferred pair is
**Claude first and Codex second**, set on 2026-10-25 and clarified on 2026-10-28. A round has two
reviewer seats. The maintainer records this policy in the local reviewer-tooling file; account
details, commands, live quotas and shared state stay on that machine.

| preferred seat | when to use a fallback | fallback order |
|---|---|---|
| Claude | its account quota is exhausted | Grok, then agy |
| Codex | its existing below-15% reserve rule applies | Grok, then agy |

Keep usable preferred reviewers first. Fill only eligible empty seats, in seat
order, skipping any family already used. If both are limited, use Grok + agy;
one family never fills both seats. Do not wait for a reset or ask for approval.
Return each preferred reviewer before its next launch after its own confirmed
full reset to 100%; keep any valid review already running or completed.

Claude's quota state is separate from Codex's. Use fresh provider usage/limit
evidence, with the account and affected windows recorded. A cached reading,
context meter, usage-read error or expected reset time is not proof of quota
exhaustion or a full reset. Keep proven reserve until every affected window has
fresh full-reset evidence. If that evidence is not available, keep the fallback
and continue; record the gap and report it once after the expected reset time.
That report is not an approval stop. A real account usage-limit rejection of a
Claude turn can start reserve; it cannot prove a reset. Claude has no new 15%
trigger in this correction.

Read the current Codex account quota before each reviewer attempt and round. Use the lowest
remaining percentage across its applicable windows. **Below 15% remaining**, keep Codex in
reserve and use **Grok, then agy** if Grok cannot return a valid review. Exactly 15% does not
start reserve. Once reserve starts, keep that mode across sessions until every window that caused
it has fresh evidence of its own full reset to **100%** (a full reading or explicit provider proof
of a full refill before later usage), and no applicable window is still
below 15%. Then return to Codex before the next reviewer launch. A partial recovery, a different
window's reset, or an expected/advanced reset time alone is not enough. Shared use can hide the
full reading; keep reserve and record that evidence gap if a full reset cannot be proved.

Remaining quota is 100 minus the service's used percentage. It is not context capacity.
Keep the account/window identities and reset evidence in a shared retained handoff, with safe
updates by concurrent agents. Unknown data or a service denial is not numeric proof of low quota or a full reset. A failed
fresh read never permits Codex. Restore lost state, or use a fresh same-account read showing all
applicable windows at 100%, to recover normal mode.
Grok and agy may replace either quota-blocked seat under the table above. If a
seat cannot be filled, record it and continue with the eligible families left;
do not spend the Codex reserve or count a fallback twice. Zero valid legs is a stop.
Keep the existing validity, effort, family and zero-reviewer stop rules.

## What it is for

Ordinary engineering discipline, written down so an agent cannot skip it. Work in slices with one
scope each, independently testable and revertible. Every step gets a recorded state and evidence;
BLOCKED never advances. A missing reviewer leg is reported degradation; zero legs is a stop.

The default `dmf` and the full flow review the plan and a separate test plan before implementation. Tests go red before
they go green, every project gate category gets its own result, and the complete change gets a
final review. Deliver through a merge or pull request, define rollback before deployment, and
prove the result. Docs-only delivery records "docs only, no runtime surface".

At each completed slice and at task completion, after the required checks, reviews, delivery and
proof, finalize a dated implementation report in the plan's retained working copy. Define that
durable path before review. A tracked plan includes known facts and a pointer to a retained working
copy outside the tracked tree before the final review freeze. That pointer and the handoff give
access or restore steps. Post-merge facts go in that copy without repeated report-only merges.
Keep the reviewed plan bytes and
the source, decisions, check evidence, deployment/rollback facts and follow-up instructions needed
to return to the task. After saving and verifying those records, remove the task's no-longer-needed
temporary files, isolated caches, builds and test resources. Check ownership and current use first.
Keep live/shared resources and required evidence, and record cleanup results and reasons for
anything retained. A blocked or READY_FOR_DEPLOYMENT handoff updates the same report with the real
state, kept resources, next responsible actor/action and cleanup condition; resume it when proof succeeds.
Cancelled or abandoned work records that outcome and uses the same retention and safe-cleanup rules.
Use `dsf` for this completion phase even after a `dmf` or full-flow task. Reuse its plan and completed gate/review
evidence; keep its required delivery proof and all retention and cleanup safeguards.
When no tracked content changes, this phase needs no new slice, MR or review cycle; record it in
the task report. A tracked edit follows its own flow, review and delivery rules.

**Independent means one leg per model family**, on the same frozen artifact, with full access,
separate outputs and no conversation between legs. Resolve the newest model at run time; where
effort can be set, choose and record it. Check what actually answered. A clean exit alone is not
proof that a review happened. **DO MORE IN EACH ROUND** asks for about 30% more active work: check a risk map
before the freeze, then ask every leg for its whole-artifact review and a second pass that tries
to break the map's unproved claims. The map never limits access.

**PRODUCT CONVERGENCE** ends full-flow review after two consecutive rounds with zero findings in
the tracked change set. Findings in gitignored process artifacts go to the backlog with a trigger;
they do not buy more rounds. In full flow, the cap is five rounds per artifact. A cap never turns an
unreviewed correction into a reviewed one; reaching it with such a correction is a stop.

**RELEASE CANDIDATE FIRST** limits scope while an app or service cannot yet run and do its main
job. Build only what brings it closer; file the rest for later, security, stability and safety
first. If the owner asked for such work, put it to them. This removes no test, gate or review.
Step 6 also says reuse before building and ask before widening. Its approval list is explicit:
another product, authentication, permissions, a database, a dependency or a public API needs
owner approval when it was not part of the task.

**USE THE LATEST VERSION OF EVERYTHING** applies to versions a slice adds, upgrades or pins.
Look up the newest stable release and its use, confirm against a version-exact source, and declare
an exact version. Untouched pins stay put. Step 3 defines the defect and compatibility exceptions;
an explicit owner pin wins. Existing dependency upgrades get their own slice. AI model choice
and reviewer effort follow their own policies.

Step 2 also asks four design questions where software changes: input checks and
data types, logic apart from side effects, retries and partial failure, and safe
ownership of shared state. Record answers or reasons that a question does not
apply in the existing plan, also in `dsf`. Clear existing code can stay; step 6
still limits scope.

`TOOLING.md` describes an optional complexity/duplication trial on one project,
inspired by selected `ub-mode` ideas. Measure useful and false findings, time,
memory and disk use, then let the agent choose and record the supported action
within already authorized work. Routine design, test and project-check decisions
need no separate owner approval. Existing scope, test, review, delivery and real
blocker rules still apply. There is no global score requirement or automatic
tool installation.

**MR SIZE** gives related tests up to 2,000 changed lines, added plus deleted, where the project's
size rule counts tests. Everything else keeps the project's budget; its exceptions apply to both.
Record both counts in the merge request and split related tests above their budget.

**STUDY YOUR OWN WORK** records an owner correction, an escaped finding or a `postmortem-fix` run
as a lesson candidate; otherwise record `NO_ENTRY` with the checks. The main session checks the
evidence before accepting a lesson. Before planning, read `experience/INDEX.md` and matching entries
as hypotheses to re-check. Lessons never outrank written rules; harness changes take a later slice,
and protected rules can only be proposed to the owner. There is no size cap on always-on instructions.

**AUTO-DECIDE AFTER ONE HOUR** applies to a closed set of options with a named recommendation,
after an hour with no owner message. Record the choice and when it fell due. The exclusions still
hold: external effects or hard-to-reverse actions, exposed credentials, owner-only credentials or
permissions, scope decisions, an option the agent would refuse, or no recommendation. Harness changes are excluded.

## Flow modes: `dmf` is the default

| mode | plan review | separate test-plan review | final change review |
|---|---|---|---|
| `dmf` — do medium flow (default) | 2–3 rounds | 2–3 rounds | 2–3 rounds |
| `dsf` — do the simpler flow | dropped | dropped | exactly 2 rounds |
| full flow | original re-review rules | original re-review rules | original re-review rules |

A round uses the normal reviewer legs; it is not one reviewer. `dmf` keeps the
full twelve steps, full plan, separate test plan, tests before code, all gates,
delivery proof and cleanup. Each stage has two required rounds and its own cap of three. Round 2
reviews round 1's corrections. If round 1 changed nothing, round 2 is a fresh
whole-artifact review with its ledger. All three `dmf` stages stay required even
for explicitly selected `dmf` on prose: the separate test plan covers document checks. Two clean rounds and
the full-flow five-round cap do not apply to `dmf`.

Resolve findings and run the required checks. Any material change to the reviewed scope, design,
test strategy, code or proof claims after round 2, from review fixes, gate results
or the author, requires round 3 on the corrected
artifact and its delta. Otherwise the stage finishes after two rounds. A refusal
or missing leg alone uses existing retry/degradation rules, not an extra round. Recording counts, dispositions, evidence paths and later observed facts that do
not change those decisions or claims is bookkeeping; it does not trigger round 3.
Existing retained-report and tracked-edit delivery rules still apply. A later material in-scope amendment to a stage that
closed at two uses its remaining third round before advancing with it or delivering
it. Record each stage's actual count, cap and reason in the plan, finding register, MR
and final report: six to nine rounds in total.
The owner raised the `dmf` cap on 2026-10-28; completed rounds and valid reviews stay.
Before the next launch or stage advance in an undelivered slice, use an unused
third round for any currently unreviewed material change after round 2, even one
made before this update. Keep its old marker as history and append the new review
result. Already delivered tasks are not reopened solely for the new budget.

List material corrections after round 3 in the plan, relevant register and MR as "fixed
after the third review, not re-reviewed", with their stage, paths and checks. The
cap adds no fourth round or approval wait solely because the budget ended.
In-scope amendments update the plan and test strategy, use remaining stage rounds,
and disclose changes after the cap to remaining stages. Do not reset budgets to
buy more rounds. Real blockers, scope limits, reviewer validity and tests-first
still apply. `dsf` keeps its two final rounds; full flow keeps its original cap.

An explicit owner mode for the current task wins, including for documents. A
specific owner-approved project regime or owner-ordered queued mode remains unless
the current task overrides it; keep its recorded artifacts and cap behavior
within its scope. Automatic prose-only `dsf` stays unless the owner expressly
included prose in that exception or chose a mode for the current task.
Agent-written "full flow" labels from standing binary `dsf`/full rules that
only mean "not dsf", generic full-flow boilerplate and older general full-over-`dsf`
preferences use this newer default for new slices. A specific owner
choice of the full review regime stays full.
Otherwise prose-only tasks and eligible simple work keep `dsf`. All other work,
including big tasks, uses `dmf`. Ask for "full flow" to use the original cap,
re-review and convergence rules. Record the selected mode and trigger in the
plan and MR. Slices already running when this rule takes effect keep their recorded mode
unless the owner changes it, including their mode's own eligibility checks.
When automatic prose-only `dsf` gains executable work, record its real state and
continue in a new software slice within the authorized task, `dmf` by default.
Keep the prose review history; it does not count as software-stage reviews.
The software slice gets its own plan, test-plan and final-change reviews. This
is new executable scope, not a budget reset for the same scope.
Step 12's report and cleanup phase always uses `dsf`.

## The simpler flow: `dsf`

Use the selection order above. Without an explicit owner mode, `dsf` stays on for prose-only changes. The owner can also request it directly or through the queue.
The final report and cleanup phase also uses `dsf`, including after a `dmf` or full-flow task.
Runnable examples are not docs-only. The agent may choose `dsf` for simple work of a few commands.
Shipping code, tests, configuration, process or launcher scripts, step 6's approval list, outward-facing
or hard-to-reverse work are not simple. If in doubt, use the default `dmf`, unless the owner selected another mode. Record the trigger in the plan
and MR, or in the existing task report for completion work with no tracked content change.

Write one short plan, including step 2's design answers for software changes, temporary
resources, safe-removal checks and the retained
working-plan/report and evidence paths. There is no plan review or separate test-plan review.
There are exactly two final review rounds with the normal reviewer legs. Tests still come first
with the red recorded; for docs-only work step 8 is NOT TRIGGERED. Run every project gate before
review and after any fix. Fixes after the second round are listed as "fixed after the second review,
not re-reviewed". Re-review, its cap and the two clean rounds of product convergence do not apply.
Delivery and its proof stay. Dropped steps are "dsf: not run", never PASS.

## On the token budget

`TOKEN-BUDGET.md` is here because its rules are rules *about this flow*. Its governing line is
**cut what a brief repeats, never what a reviewer can see**. Reviewer access and complete evidence
stay intact. Normal budgets warn and escalate; they never terminate a valid leg. A separate fuse
for a broken loop records INVALID / INCOMPLETE, never PASS.

It carries a measured baseline from one real slice — and **section 0 is where to start**, because
it lists what the previous revision got wrong. Ignoring cache reads broke both the reported total
and the input:output ratio: cache reads were 93% of input on the measured Google leg. Later
corrections in sections 2 and 3 explain why printed CLI totals are not the full spend.

No saving may be claimed until section 3's attribution exists. Record numbers as measured,
`UNAVAILABLE`, or estimates with their method. A zero must never mean "we did not look". Report
token savings and cost savings separately; failed attempts still count. Quality is known-defect
recall, not the number of findings, and each optimisation must be reversible.

`token-economy-common.md` sets out the generic design: fresh sessions, compact handoffs, evidence
on disk, read-on-demand context, telemetry and quality checks. Its small-kernel target is not a
size cap on this flow's always-on instructions; `TOKEN-BUDGET.md` calls its own kernel an experiment.

## Scope

The delivery flow is a set of instructions. The repository also has an optional,
read-only telemetry pilot. It runs from this checkout with its declared Python 3.15.2 runtime and
measures saved Claude and Codex logs. The machine profile can name a separately
validated compatibility runtime for read-only measurement. See [the pilot guide](docs/DFLOW-PILOT.md)
for the command, its evidence limits, and the parts of dflow that are still deferred.
The reader reports usage; the active flow procedure governs how agents reuse
native tools and collect measurements. No execution engine runs the stages.
