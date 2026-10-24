# delivery-flow

A mandatory 12-step delivery flow for AI-assisted software work, with `dsf` for simpler work,
independent reviewer rules, and token-budget rules that cut repetition while keeping full access.

| file | what it is |
|---|---|
| `DELIVERY-FLOW.md` | the flow: twelve steps, what each requires, and what counts as DONE |
| `REVIEWING.md` | how to run the reviewer legs steps 4 and 11 require |
| `TOKEN-BUDGET.md` | measured review costs, corrections, and rules for cutting waste without cutting the review |
| `TOOLING.md` | documentation and browser tools, reviewer capabilities, and what is lost without them |
| `token-economy-common.md` | a generic design for context, evidence storage, telemetry, and token, cost and quota control |
| `README.md` | this map and the adoption notes |

In `DELIVERY-FLOW.md`, **I** and **me** are the person who adopts the flow; **you** is the agent
working for them.

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

**Then write a local reviewer-tooling file that this repository deliberately does not contain**:
which families are primary or substitutes, how many legs run, the tools, paths and tiers, and how
each fails. Record invocations, validity checks and availability probes. Name its path in the
project's instruction file and load it the same way. Keep it local — accounts and quotas belong
to your machine. `TOOLING.md` is the reference, never that profile.

The flow decides **whether** a step is required and **what counts as done**. Your project decides
**how it is spelled** — commands, paths, gates, integration branch. Where they conflict on a command
or a path, the project wins. Where the project would remove a step, the flow wins and the conflict
is a stop.

## What it is for

Ordinary engineering discipline, written down so an agent cannot skip it. Work in slices with one
scope each, independently testable and revertible. Every step gets a recorded state and evidence;
BLOCKED never advances. A missing reviewer leg is reported degradation; zero legs is a stop.

The full flow reviews the plan and a separate test plan before implementation. Tests go red before
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

**Independent means one leg per model family**, on the same frozen artifact, with full access,
separate outputs and no conversation between legs. Resolve the newest model at run time; where
effort can be set, choose and record it. Check what actually answered. A clean exit alone is not
proof that a review happened. **DO MORE IN EACH ROUND** asks for about 30% more active work: check a risk map
before the freeze, then ask every leg for its whole-artifact review and a second pass that tries
to break the map's unproved claims. The map never limits access.

**PRODUCT CONVERGENCE** ends full-flow review after two consecutive rounds with zero findings in
the tracked change set. Findings in gitignored process artifacts go to the backlog with a trigger;
they do not buy more rounds. The default cap is five rounds per artifact. A cap never turns an
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

## The simpler flow: `dsf`

`dsf` is on at the owner's request (also through the queue), and always for prose-only changes.
Runnable examples are not docs-only. The agent may choose `dsf` for simple work of a few commands.
Shipping code, tests, configuration, process or launcher scripts, step 6's approval list, outward-facing
or hard-to-reverse work are not simple. If in doubt, use the full flow. Record the trigger in the plan and MR.

Write one short plan, including temporary resources, safe-removal checks and the retained
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

These are instructions, not a framework. There is nothing to install and nothing to run.
