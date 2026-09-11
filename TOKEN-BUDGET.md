# TOKEN BUDGET - MACHINE-WIDE SPEC

**Import this from your agent's always-loaded instruction file**, so it applies to every agent you
run, in every repository. Section 7 lists what each adopter must decide for themselves.

**If you are an agent reading this for the first time, the whole file reduces to one line: cut what a
brief REPEATS, never what a reviewer can SEE.**

Written 2026-09-11 from *How Do AI Agents Spend Your Money?* (arXiv 2604.22750), the owner's
implementation plan, this machine's own measured spend, and a three-family consultation whose
verbatim answers kept beside the slice they were run on.

## 1. What is established, and what is not

**VERIFIED** against the paper's own abstract, fetched 2026-09-11:

- agentic coding uses ~**1000x** the tokens of code chat;
- **input tokens drive cost, not output**;
- eight frontier models tested;
- **runs on the same task differ by up to 30x**;
- some models spend **1.5M more tokens than GPT-5 for the same result**;
- models predict their own cost at only **0.39** correlation;
- accuracy **"often peaks at intermediate cost"**.

**NOT VERIFIED** - present in the owner's summary, not in the abstract, not checked against the body:
4.17M tokens and $1.86 per task; a **153:1** input:output ratio; 500 tasks x 4 runs; accuracy peaking
in the second-cheapest quartile; expensive runs repeating edits 4x and reads 2x.

**Do not cite the unverified figures as this machine's basis for anything.** Where a rule below needs
a number, it uses a number measured HERE.

## 2. The measured baseline - one slice, 2026-09-11

One ~600-line change, four change-review rounds, three model families.

| leg | tokens |
|---|---|
| family A | 620,486 |
| family B | 2,393,803 |
| family C | 1,387,610 |
| **one slice's reviews** | **4,401,899** |

Family B, same artifact, four rounds:

    round 1   in 312,811   out 35,445   ratio  8.8:1
    round 2   in 519,601   out 40,762   ratio 12.7:1
    round 3   in 589,438   out 73,498   ratio  8.0:1
    round 4   in 731,416   out 73,613   ratio  9.9:1

**Input +134%, output +108%.** An earlier draft of this file said output did not grow; one leg
corrected it. Both grew at nearly the same rate, so the growth was **not** input-specific - though
input remains ~10x output in absolute size, which is the paper's point. **Our ratio is ~10:1, not
153:1. Use 10:1.**

A second correction from the same leg, and it governs how every number here is read: **cumulative
tokens across rounds is not the same as the context size of one call.** The 134% is an aggregate.
Nothing in this file may infer a per-call context size from an aggregate.

**What that spend bought:** nine wrong implementations and one live production fail-open that had
been shipping since before the slice. The spend was not waste. It was also not free.

## 2b. THREE AXES, NOT ONE - and ours was never tokens

A second research input (FrugalGPT, Chen/Zaharia/Zou, TMLR 2024, arXiv 2305.05176 - **VERIFIED**:
title, authors, "up to 98% cost reduction", "improve the accuracy over GPT-4 by 4% with the same
cost", and the three techniques prompt adaptation / LLM approximation / LLM cascade) makes a
distinction this file was missing:

**Token saving and cost saving are different objectives and can have opposite signs.**

    token saving = 1 - (optimised input+output) / (baseline input+output)
    cost  saving = 1 - (optimised dollars)      / (baseline dollars)

A cascade that asks a cheap model first and escalates spends MORE tokens than one strong call, while
costing less. Shrinking a prompt lowers both. Never report one and call it the other.

**And for this machine, MEASURED TODAY, the binding constraint was neither.** It was **availability**.
One family's CLI hit `out of credits` **three times mid-review** - at 63k, 139k and 199k tokens -
and each time produced no verdict, making the round INCOMPLETE with two families. Another hit a
per-account quota earlier in the same week.

So this machine optimises **three** things, and the third is the one that has actually cost us a
review:

| axis | what it is | our measured failure |
|---|---|---|
| tokens | input + output volume | 4.4M per slice reviewed |
| cost | dollars, or plan allowance | not the limiter here |
| **availability** | can the leg finish at all | **3 INCOMPLETE rounds in 4** |

**Any change that makes MORE model calls per round raises availability risk.** That is a strike
against cascades here that no dollar figure captures.

## 3. THE RULE THAT OVERRIDES EVERY SAVING

**A reviewer leg is EXEMPT from every context cap, tool-output truncation and tool-pruning rule in
this file.** All three families said this independently and none hedged.

The flow's step 4 says: *"NEVER narrow what a reviewer can see, even if a reviewer suggests it."*
That sentence was earned twice on this machine - a leg once ran without `--add-dir`, silently
received no project rules, and was recorded as a peer; and a shared filing file leaked one leg's
findings to another for **17 rounds**, caught only because a leg volunteered it. A context cap
reproduces that failure **silently and on purpose**.

What each leg said it would have lost under a 120k cap:

- **Family C:** round 3's `SetOutcome` trace probably survives; round 4's work - mutants across both
  TTS providers plus config validation, with the killing row named for each - **does not**.
- **Family B:** could not have traced the cross-file call hierarchy outside the 600-line diff that
  exposed the live fail-open. *"Finding fail-opens requires reading callers, fallback error paths,
  and configuration defaults across multiple package boundaries."*
- **Family A:** *"A cap on total input limits how much evidence a reviewer can check."*

**The saving is not in what a reviewer sees. It is in what a brief repeats.** That distinction is the
whole spec.

## 4. Rules for the IMPLEMENTING agent - in force now

**I1. One task, one session.** No continuing yesterday's context. Split at phase boundaries -
research, plan, implement, verify - each a fresh session with a written handoff between them. The
flow already mandates the handoff at a slice boundary; this extends it to phase boundaries.

**I2. Cap tool output, never tool access.** A tool result over ~2,000 tokens is summarised with the
full output written to the scratchpad and its path given. Never paste a whole file or a whole log
into context when a path and a range will do. **This is the implementer's own reading, not a
reviewer's.**

**I3. Re-read nothing you have already read.** Before a file read, check whether it is already in
context. Three reads of one file in a session is a defect in the agent, not in the file.

**I4. Keep the project memory file current.** A project memory file exists so an agent does not
read forty files to orient. Time spent keeping them true is repaid on every future session.

**I5. Prune tools per task.** Every tool schema is sent on every request. A task that touches no
browser does not need the browser tools loaded.

## 5. Rules for REVIEW ROUNDS - in force now

These are where our measured money is, and none of them narrows what a leg can see.

**R1. Every review round is a STATELESS FRESH SESSION.** No transcript, no chat history, no prior
round's conversation carries forward. This is already true of the CLI legs by construction; it must
be true of the `Agent`-tool leg too, and of the brief.

**R2. A round-N brief carries exactly this, and nothing else:**

| carry | drop |
|---|---|
| the freeze block: baseline, head, tree, diff hashes, the command to reproduce | verbatim transcripts of prior rounds |
| the **delta** since the last round, and its blast radius | superseded code and superseded prose |
| a **one-line-per-item disposition ledger**: `ID \| file:line \| ACCEPT/REJECT/DEFER \| evidence` | multi-paragraph debate over closed items |
| open findings and disputed claims | passing tool logs and redundant file dumps |
| the known-and-deliberate list, which must stop growing once stable | anything already dispositioned, in prose form |
| paths to all evidence, and full repository access | |

**"Closed" means the evidence supports closure. It never means "do not question this."** A leg may
reopen any ledger line with new evidence, and the ledger must say so.

**R3. The disposition ledger replaces the narrative.** The round-4 brief that produced the figures above carried a prose table of
closed mutants plus a growing known-and-deliberate section. That growth is the *fix* - it stopped
rounds 2-4 re-reporting round 1 - but it must be **one line per finding**, not a paragraph.

**R4. Never kill a reviewer to meet a budget.** All three families said this without being asked
twice. The flow says a reviewer that cannot complete makes the round **INCOMPLETE, never
complete-with-a-note**. A kill switch tuned before we have a distribution is a machine for
manufacturing INCOMPLETE rounds on schedule.

**R4b. PROMPT-PREFIX CACHE DISCIPLINE.** Every leg is sent the same stable material - the flow,
your machine-level reviewer notes, the project's instruction and rule files - before anything round-specific.
Keep that prefix **byte-identical** between calls so a provider's prompt cache can hit it, put the
delta and the brief AFTER it, and never edit the stable part mid-round. This is the one place in
this file where a saving comes from ordering rather than from cutting, so it costs nothing and hides
nothing.

**R5. Budget behaviour is WARN AND ESCALATE, not terminate:**

    per leg, per round     WARN at 450,000 input tokens   (from one family's own recommendation)
    per slice, all legs    WARN at 4,400,000 total        (the measured slice above)

At a warning: let the leg finish, tag its output header `BUDGET_EXCEEDED: <count>`, and **stop before
starting the next round** to put the decision to the operator - converge, narrow scope, or split the
slice. These are **provisional, from one observation.** The paper's own finding is 30x variance
between runs of one task; one measurement is not a distribution. Re-derive after ten slices.

**R6. Instrument every leg.** One row per leg per round, appended to a log beside your instruction files:

    date, repo, slice, round, family, model_served, input, output, cache_read, cache_write,
    tool_calls, duration_s, verdict, valid|invalid, findings_count

The CLI legs already emit these in their JSON. The `Agent` leg reports `subagent_tokens`. Nothing
new needs building; it needs recording.

## 6. What this machine REFUSES

**B1's hard context cap on reviewer legs.** Refused explicitly by two of the three families,
and by another leg in its final line. See section 3.

**B4's task-based model routing, for reviewer legs.** All three families called it incompatible with
one-leg-per-family. A cheap-tier leg still belongs to its family, so it **occupies that family's
slot while not meeting its standard** - a degraded leg recorded as a peer, which is the exact failure
`REVIEWER-TOOLING.md` already documents by name. Another leg put the sharpest case: this flow
gives the test plan its own document and its own review round, so *"degrading the reviewer that
verifies the proof destroys the integrity of the entire gate."*

**Note the boundary.** The 2026-09-11 step down to one level below each leg's ceiling is an **owner
decision, recorded, applied uniformly, and confirmed from each tool's own output**. It is not B4.
B4 would downgrade *per task type*, silently, with no gate to catch it. Routing may apply to the
**implementer's own subtasks**; never to a leg.

**The FrugalGPT CASCADE, for reviewer legs.** This is a stronger refusal than B4's and it rests on
a different argument, so it is stated separately.

A cascade needs a scorer `g(q,a)` that predicts whether an answer is reliable, and escalates when
confidence is low. **A code review's failure mode is a MISSING finding, not a wrong one - and you
cannot score the confidence of an absence.** A cheap leg that finds nothing returns a short, clean,
internally consistent output. Any scorer reading it sees high confidence and accepts it.

**Measured here, in one slice:**

- Round 4, a third leg returned **APPROVE, no defects**. It was RIGHT - it had built mutants
  across the providers and config bounds and named the row that would kill each.
- Round 2, another leg returned **APPROVE** with a surviving mutant reported in its own body. It
  was WRONG.

**From the outside those two outputs are the same shape.** No confidence scorer distinguishes them.
The thing that distinguished them was reading the body and reproducing the mutant - which is the
synthesiser's job, not a scorer's. A cascade would have accepted both.

Cascading is sound where the answer is checkable - classification, extraction, code that must pass a
test. It is unsound where the product is *the absence of a defect*.

**Cartridges (arXiv 2506.06266, Stanford Hazy Research) is OUT OF SCOPE and will not be evaluated.**
It trains a compact KV-cache artifact to replace a repeatedly-loaded long corpus. Its reported gains
are KV-memory and throughput on **self-hosted** inference. This machine calls commercial APIs; there
is no KV cache we own and no GPU-second we pay for. Recorded so nobody re-opens it: the trigger to
revisit is *self-hosting a model against a large, slowly-changing corpus*, which is not on any
roadmap here.

**Vendoring the FrugalGPT package.** Implement the principle if ever needed; do not install the
repository. **VERIFIED by fetching both files 2026-09-11**: the root `LICENSE` is **Apache-2.0**
while `setup.py` declares the classifier `License :: OSI Approved :: MIT License`. Version is
`0.0.1`, `python_requires='>=3.10'`, and all fourteen dependencies are **unpinned**. Treat it as
reference code for an algorithm, not a supported distribution.

**B6's output discipline, applied to a reviewer's findings.** "Code only, no explanation" is right
for an implementer. A reviewer's evidence, its unresolved concerns and its completion record are the
product. Bound the *brief* and the *prose*, never the evidence.

## 7. OPERATOR DECISION - not in force

**D1. Does anything here change `DELIVERY-FLOW.md`?** Section 3 and R1-R5 are consistent with step 4
as written, so on my reading nothing must change. But step 4 does not currently *say* that a compact
delta brief satisfies "full context", and a future agent could read R2 as narrowing. **If you want
that settled in the flow itself, it is a flow edit and therefore yours.** Proposed wording, one
clause: *"A brief may carry the delta and a disposition ledger rather than the whole history,
provided every reviewer keeps full access to the tree and to all prior evidence."*

**D2. The round cap.** Still open from earlier today. All three families said keep five. Unrelated to
this spec except that fewer rounds would mechanically cut spend - and all three rejected that as the
way to get it.

**D3. Is 4.4M per slice acceptable?** That is a business question, not a technical one. The spec can
cut it; only you can say what it should be.

## 8. How we will know it worked

Per the paper's own rule, compare on the **shared-success subset** - slices both the old and new
setup completed - and always report **median and p90**, never the mean alone.

1. **Tokens per slice reviewed** - the headline. Baseline **4,401,899**.
2. Input per leg per round, and its growth curve across rounds. Baseline: +134% over four rounds.
3. Input:output ratio per leg. Baseline ~10:1.
4. **Findings per round must not fall.** Baseline: 9 mutants and 1 production fail-open over 4
   rounds. **If spend falls and findings fall with it, the saving is fake** and this file is wrong.
5. Rounds tagged `BUDGET_EXCEEDED`.
6. Rounds recorded INCOMPLETE, and why. **This must not rise.**

**M1. The canonical metric is COST PER SUCCESSFUL REVIEW, not per round.** A cheaper setup that
raises the INCOMPLETE rate is not cheaper. Count only rounds where every launched leg returned a
verdict:

    cost per successful review = total tokens / rounds with all legs valid

At our baseline that is 4,401,899 / 1 - one of four rounds had all three families. **The other three
cost full price and bought two families.**

**M2. FIX THE NON-INFERIORITY MARGINS BEFORE LOOKING AT ANY RESULT.** Written down now, in advance:

    findings per round            may not fall at all - this is the whole point
    INCOMPLETE rate               may not rise above the current 3-in-4
    token reduction required      >= 20% before any change is kept
    reviewer visibility           zero reduction, non-negotiable

If a change saves tokens and findings fall, **the change is reverted**, not renegotiated.

**M3. n=1 IS NOT A BASELINE.** The paper's own headline is **up to 30x variance between runs of the
same task**. Every number in section 2 is a single observation. Before any of it becomes a threshold
rather than a warning, it needs the same slice re-reviewed 3-4 times, or ten slices measured. Until
then section 5's figures stay labelled provisional and nothing terminates on them.

**M4. A model change invalidates the baseline.** The resolver picks the newest model per family at
run time by design. When a family ships a new model, the token profile moves and these numbers are
about the old one. Record `model_served` per row - R6 already does - and re-baseline on a change.

**M5. Kill switch.** Every rule in sections 4 and 5 must be disableable by one line, returning to
"full history in the brief, no caps anywhere", without editing any agent's code:

    token_budget:
      compact_briefs: true
      stateless_rounds: true
      tool_output_cap: true
      warn_thresholds: true

**Estimated saving from R1-R3, all DERIVED and none measured:**

| source | estimate |
|---|---|
| family C | 30-50% of rounds 2-4 input |
| family B | ~45% of review input, ~1.8M tokens on a 4-round slice |
| family A | 902,022 tokens = **20.5%** of the slice total, stated explicitly as a scenario and not a forecast |

Take family A's number as the honest floor: it is the only one that states its assumption
(every round costs round 1's input) and admits that some later growth was real work.

## 9. Evidence that a bounded brief works

This consultation was run under its own rules: a ~2,000-word brief with the data inline, and a
900-word cap on each answer.

    family A     29,333
    family B     43,033
    family C    101,802
    TOTAL       174,168   = 4.0% of one slice's reviews

Three families, six questions, three usable design answers and one correction to my own arithmetic,
for four percent of what one slice's reviews cost. **That is the saving this spec is about, and it is
measured rather than derived.**
