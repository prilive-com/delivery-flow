# TOKEN BUDGET - MACHINE-WIDE

**Status: IN FORCE, operator decision 2026-09-11. Revision 2, same day.** Imported from
`~/.claude/CLAUDE.md`, so it applies to every agent on this machine, in every repository.

**The governing rule, unchanged and overriding everything below:**

> **Cut what a brief REPEATS; never cut what a reviewer can SEE.**

Reviewer legs keep full repository access and full evidence access. A leg terminated for exceeding a
token budget is never a successful leg.

**The goal is not fewer tokens at any cost.** It is to remove repeated transport and wasted context
while preserving a reviewer's ability to investigate exactly as deeply as before.

---

## 0. WHAT REVISION 2 RETRACTS

Revision 1 reported this machine's review spend as **4.4M tokens** for one slice and its
input:output ratio as **~10:1**. Both were wrong, and wrong in the same way: **they counted only
`input_tokens` and ignored `cache_read_tokens`.**

Measured on the Google leg, the one family that reports the field:

| round | fresh in | cache read | TOTAL IN | output | in:out |
|---|---|---|---|---|---|
| 1 | 312,811 | 4,162,496 | 4,475,307 | 35,445 | 126:1 |
| 2 | 519,601 | 8,546,668 | 9,066,269 | 40,762 | 222:1 |
| 3 | 589,438 | 7,440,038 | 8,029,476 | 73,498 | 109:1 |
| 4 | 731,416 | 7,538,704 | 8,270,120 | 73,613 | 112:1 |
| **all** | **2,153,266** | **27,687,906** | **29,841,172** | **223,318** | **134:1** |

**Cache-read is 93% of everything that ever entered that model.** The real figure is **13.9x** what
revision 1 reported, for one leg alone.

So: **the claim "our ratio is ~10:1, not 153:1" is retracted.** Our measured ratio is **~134:1** -
the same order as the paper's, not a different world. Revision 1 used that false contrast to argue
this machine's economics were unlike the study's. That argument is withdrawn.

**Cached tokens are still context tokens.** They are cheaper per token, not free, and they are what
the model actually reads.

---

## 1. ESTABLISHED EVIDENCE

### 1.1 Stanford agent-cost study - VERIFIED FROM THE FULL PAPER

*How Do AI Agents Spend Your Money? Analyzing and Predicting Token Consumption in Agentic Coding
Tasks*, arXiv 2604.22750, April 2026.

**Revision 1 marked several of these NOT VERIFIED because it had read only the abstract. The full
paper was fetched and read on 2026-09-11 and carries them.** Verified by locating each in the text:

| claim | status |
|---|---|
| ~**4.17M** tokens per agentic task | VERIFIED, full paper |
| **$1.857** average task cost | VERIFIED, verbatim in Figure 1 |
| **~153.85:1** agentic input:output ratio | VERIFIED, full paper (Figure 1) |
| **500** SWE-bench Verified problems | VERIFIED, "each vertical bar represents one of the 500 SWE-bench tasks" |
| **four** independent runs per task | VERIFIED, "four independent runs" |
| **eight** frontier models | VERIFIED, "eight frontier LLMs" |
| ~1000x the tokens of code chat | VERIFIED, abstract |
| up to **30x** variance between runs of one task | VERIFIED, abstract |
| models self-predict cost at only **0.39** correlation | VERIFIED, abstract |

### 1.2 A correction to how the repeated-action finding is described

Revision 1 described expensive runs as doing "repeated file edits 4x more and repeated file reads
2x more". **That is wrong.** The paper's own caption reads:

> *Relative frequency of repeated file modifications (a) and repeated file views (b) across cost
> quartiles, compared to the minimum-cost setting and estimated via **mixed-effects regression***.

These are **regression coefficients relative to the minimum-cost quartile**, not raw frequency
multiples. The same is true of the accuracy result: *"Relative agent accuracy across cost quartiles,
compared to the minimum-cost setting and estimated via mixed-effects regression."* Cite them as
associations estimated under a model, never as "N times more".

### 1.3 Stanford's ratio is not our ratio

**Do not use 153.85:1 as this machine's figure**, and do not use ours as theirs. Different harness,
different workload. Ours is measured in section 2 and is currently ~134:1 on the one leg that can be
decomposed.

### 1.4 FrugalGPT - VERIFIED

arXiv 2305.05176, Chen/Zaharia/Zou, TMLR 2024. Abstract confirms "up to 98% cost reduction",
"improve the accuracy over GPT-4 by 4% with the same cost", and the three techniques. Repository
fetched: root `LICENSE` is **Apache-2.0** while `setup.py` declares an **MIT** classifier; version
`0.0.1`; fourteen unpinned dependencies. Reference code for an algorithm, not a distribution.

---

## 2. THE MEASURED BASELINE, AND WHAT CANNOT BE MEASURED

One ~600-line change, four change-review rounds, three model families.

### 2.1 What each family actually exposes

**This is the limiting fact for everything in section 3.** Measured by reading each tool's own
output:

| family | fields exposed | decomposable? |
|---|---|---|
| B (stream-JSON CLI) | `input_tokens`, `output_tokens`, `cache_read_tokens`, `thinking_tokens`, `total_tokens`, plus a per-step stream | **yes** |
| A (CLI) | one `tokens used` total, composition **unknown** | **no** |
| C (in-process agent) | one `subagent_tokens` total, composition **unknown** | **no** |

**Two of three families report a single number whose composition is unknown.** Their cache-read
share, and therefore their true context volume, is **UNAVAILABLE**. Record it that way. Do not
assume their composition resembles family B's.

### 2.2 The slice, stated honestly

| family | reported | what that number IS |
|---|---|---|
| A | 620,486 | total, composition UNAVAILABLE |
| B | 30,064,490 | fresh 2,153,266 + cache-read 27,687,906 + output 223,318 |
| C | 1,387,610 | total, composition UNAVAILABLE |

**A single slice total is not reportable**, because two of the three numbers do not mean the same
thing as the third. Revision 1 added them anyway. That is the error section 0 retracts.

### 2.3 The one attribution measurement that exists

Family B, round 4: **7,538,704 cache-read tokens over 597 recorded steps ~ 12,627 tokens of stable
context resent on every step.**

That single figure is the whole argument for section 7's kernel experiment: **the stable prefix is
multiplied by the step count.** Cutting 5,000 tokens from a prefix that is resent 597 times is worth
~3M tokens on one leg of one round. **This is a measurement of one leg of one round and nothing is
promoted from it** - see section 11.

---

## 3. TELEMETRY AND TOKEN ATTRIBUTION

The question this section exists to answer, and which no current data answers:

> **How much of our review token consumption is repeated brief and history, and how much is useful
> reviewer investigation of the repository?**

**Until that is measured, no saving figure may be claimed.** In particular the ~20% figure in
revision 1 is withdrawn until section 11's data exists.

### 3.1 The schema

One row per leg per round, appended to the token log beside the instruction files. Every field is
recorded as a number, as `UNAVAILABLE`, or as an estimate **with its method named**.

    # identity - see section 12 for why each is here
    date, repo, slice, round, family, model_served, effort, cli_version,
    toolset_hash, provider_mode, cache_mode, kernel_hash, project_instr_hash,
    compaction_behaviour

    # what WE sent, which we always know exactly
    sent_prefix_bytes, sent_brief_bytes, sent_delta_bytes, sent_ledger_bytes

    # what the provider reports
    input_fresh, input_cached, cache_write, output, thinking, total_reported

    # derived, each with a method
    prefix_tokens_est, brief_tokens_est, reviewer_initiated_est, steps

    # behaviour
    tool_calls, file_reads, file_reads_repeated_unchanged

    # outcome
    verdict, valid, findings_verified, findings_rejected, evidence_accessed_count

### 3.2 The estimation method, stated so it can be audited

**Nothing here may be recorded as measured.** Each is marked `_est`.

1. **`prefix_tokens_est` and `brief_tokens_est`** - we author these bytes, so we can count them.
   Estimate tokens at **bytes / 4** for English prose. Mark `ESTIMATED(bytes/4)`. Where the provider
   offers a tokenizer, use it and mark `MEASURED(tokenizer)` instead.

2. **`reviewer_initiated_est`** - what the leg pulled in itself. Only computable where `steps` and
   the cache fields are both available:

       reviewer_initiated_est = (input_fresh + input_cached)
                              - steps * (prefix_tokens_est + brief_tokens_est)

   **This subtraction is wrong if the provider does not resend the whole prefix every step**, so it
   is valid only for families whose stream shows per-step context. For A and C: `UNAVAILABLE`.

3. **`file_reads_repeated_unchanged`** - count reads of a path whose content hash is unchanged since
   the previous read in the same session. Measured, not estimated, where the stream records reads.

**If a field cannot be computed exactly and has no documented estimate, it is `UNAVAILABLE`. Never
`0`.** A zero that means "we did not look" is the failure this whole section exists to prevent.

---

## 4. COST IS A SEPARATE MEASUREMENT FROM TOKENS

**Token count and money are different objectives and can move in opposite directions.** Report both,
always, and never one as a proxy for the other.

    token_saving = 1 - optimised_tokens / baseline_tokens
    cost_saving  = 1 - optimised_cost   / baseline_cost

Per family and model, record: `input_fresh`, `input_cached`, `cache_write`, `output`, actual provider
cost where it can be calculated, and quota or allowance consumption where that is the real limit.

**Do not assume output is a negligible share of cost.** Output is typically priced several times
higher per token than fresh input, and cached input lower again, so a 134:1 token ratio does not
imply a 134:1 cost ratio. **No estimated output-cost percentage goes into these rules until it is
measured against our actual providers' published prices.**

Where money is not the binding constraint - a plan allowance, a credit pool - record
`quota_consumption` and say so. On this machine the binding constraint has been quota, not dollars.

---

## 5. THE RULE THAT OVERRIDES EVERY SAVING

**A reviewer leg is EXEMPT from every context cap, tool-output truncation and tool-pruning rule in
this file.** Three model families said this independently and none hedged.

Step 4 says: *"NEVER narrow what a reviewer can see, even if a reviewer suggests it."* That sentence
was earned twice here - a leg once ran without a required flag, silently received no project rules,
and was recorded as a peer; and a shared filing file leaked one leg's findings to another for 17
rounds. A context cap reproduces that failure silently and on purpose.

What each family said it would have lost under a 120k cap:

- **Family C:** one trace probably survives; the round-4 work - mutants across two providers plus
  config validation, with the killing row named for each - **does not**.
- **Family B:** could not have traced the cross-file call hierarchy that exposed the live fail-open.
  *"Finding fail-opens requires reading callers, fallback error paths, and configuration defaults
  across multiple package boundaries."*
- **Family A:** *"A cap on total input limits how much evidence a reviewer can check."*

---

## 6. AVAILABILITY PREFLIGHT

Availability is this machine's largest measured loss: legs have died **after** consuming substantial
tokens, producing no verdict. Three of twelve legs in the baseline slice were invalid for this
reason.

**Before launching each leg**, check whatever that provider exposes and record each result:

    auth_valid           | true | false | UNKNOWN
    entitlement_valid    | true | false | UNKNOWN
    model_available      | true | false | UNKNOWN
    quota_blocked        | true | false | QUOTA_UNKNOWN
    permissions_ok       | true | false | UNKNOWN
    allowance_remaining  | <number> | QUOTA_UNKNOWN

**`QUOTA_UNKNOWN` is a real and expected value. Never write "checked" for something not checked.**

A preflight that costs tokens is not a preflight. Prefer the free surfaces: a catalogue call, a
login-status call, a zero-token model probe.

**No minimum reserve is set here.** One slice cannot produce one. After enough successful runs exist,
derive a recommended starting reserve from **p90/p95 of successful-leg consumption plus a margin**,
and record the sample size beside it.

**Do not change reviewer ordering yet.** Legs continue to run independently in the current order.
Running a failure-prone family first is a plausible improvement to successful-review cost and an
unmeasured one; revisit only if the data supports it.

---

## 7. RULES FOR THE IMPLEMENTING AGENT

**I1. One task, one session.** No continuing yesterday's context. Split at phase boundaries -
research, plan, implement, verify - each a fresh session with a written handoff.

**I2. AVOID REDUNDANT UNCHANGED READS.** *(This replaces revision 1's "re-read nothing you have
already read", which was absolute and therefore unsafe.)*

Do not re-read the same **unchanged** file in full when its needed contents are still available.

**A re-read is legitimate when:**

- the file changed, or another actor may have changed it;
- the earlier context was cleared or compacted;
- exact current lines are required as evidence;
- final-state verification requires it.

**Prefer, in order:** a diff; a targeted line range; a symbol or function; the changed section. Whole
files last.

**Record repeated full reads of unchanged files as waste** (`file_reads_repeated_unchanged`). That is
telemetry, not a prohibition.

**I3. COMPLETE EVIDENCE LIVES ON DISK; CONTEXT CARRIES ONLY WHAT IS USEFUL.**

    artifact on disk = complete evidence
    model context    = only as much as is useful

Context may hold a compacted tool result. **Wherever the flow requires verbatim evidence, the
canonical artifact must still contain the complete output.** Step 8's failing test output and step
10's gate records are evidence and are never truncated on disk. Compaction that destroys them is a
defect, not a saving.

**I4. DETERMINISTIC COMPACTION BEFORE ANY LLM SUMMARY.**

Before asking a model to summarise a large tool result, do the free things first:

- strip ANSI and progress output;
- collapse identical repeated lines with a count;
- keep every failure, error and assertion message;
- keep stack traces that name project code;
- keep the command, the tool version and the exit code;
- write the full original to disk and record **its path and content hash**.

**Only if that is still too large, summarise with a model** - and then count what the summary cost.

**The net saving must include the cost of producing the summary and of any later re-hydration.** A
compaction that costs 3k tokens to save 4k, and is re-read once, saved nothing.

**I5. Keep the project memory file current.** A project memory file exists so an agent does not read
forty files to orient. Time spent keeping it true is repaid every session.

**I6. Prune tools per task.** Every tool schema is sent on every request.

---

## 8. RULES FOR REVIEW ROUNDS

**R1. Every review round is a STATELESS FRESH SESSION.** No transcript, no chat history, no prior
round's conversation.

**R2. A round-N brief carries exactly this:**

| carry | do not carry |
|---|---|
| the frozen identity block: baseline, head, tree, diff hashes, and the command to reproduce them | verbatim transcripts of prior rounds |
| the **delta** since the last round | superseded code and superseded prose |
| its **blast radius** | multi-paragraph debate over closed items |
| a **one-line disposition ledger**: `ID \| file:line \| ACCEPT/REJECT/DEFER \| evidence` | passing tool logs and redundant file dumps |
| open findings and disputed claims | anything already dispositioned, in prose |
| the stable known-and-deliberate list | |
| **paths to the complete evidence**, and full repository access | |

**A closed finding may always be reopened on new evidence, and the ledger must say so.** "Closed"
means the evidence supported closure, never "do not question this".

**R3. The ledger replaces the narrative** - one line per finding, not a paragraph.

**R4. EVIDENCE-ACCESS REPORTING.** Every leg reports, at the end of its output:

    EVIDENCE_ACCESSED
      repository paths opened:
      plans / prior review artifacts opened:
      commands executed:
      evidence files inspected:

**This is telemetry, not a quota.** No leg is required to open any particular file. Its purpose is to
separate *"the reviewer could access it"* from *"the reviewer actually examined it"* - which is the
only way to tell a cheap review from a narrow one, and the only way to know whether a saving cost us
investigation.

**R5. Budget behaviour is WARN, then ESCALATE - never terminate.** See section 10.

---

## 9. PROMPT CACHING - A COST OPTIMISATION, NOT A TOKEN REDUCTION

**Revision 1 said this "costs nothing and hides nothing". The first half was wrong.**

Keep the stable material in a byte-stable order, and put the changing material after it:

1. machine-level stable rules
2. slice-stable task capsule
3. round-specific delta

**But cached tokens are still context tokens**, and a cache write is not free. Measure, per family:

    cache_write_tokens          cache_read_tokens
    hit_ratio                   cache_write_cost
    cache_read_cost             uncached_equivalent_cost_est

**Report caching as a cost optimisation. It reduces cost per token; it does not reduce context.** The
93% cache-read share in section 0 is not a saving - it is the size of what the model reads.

**If cache writes repeatedly expire before being reused, the discipline is economically negative for
that provider** and must be reconsidered rather than kept on principle.

---

## 10. BUDGETS: A WARNING LINE, AND A SEPARATE CATASTROPHIC FUSE

### 10.1 The normal path - never terminates a valid leg

    WARN  ->  allow the leg to finish  ->  stop before the next round  ->  operator decides

A reviewer that cannot complete makes the round **INCOMPLETE, never complete-with-a-note**. A kill
switch tuned before a distribution exists is a machine for manufacturing INCOMPLETE rounds on
schedule.

**No thresholds are set here.** Section 11 says when they may be.

### 10.2 The catastrophic fuse - a different mechanism, for a different failure

A broken agent loop consuming extreme quota is not a long review. **A separate fuse may terminate
it.** When it fires:

- terminate the leg;
- record it **INVALID / INCOMPLETE**;
- **never** convert it to PASS, and never let it satisfy a round;
- preserve the transcript and all diagnostic evidence;
- handle it as any other incomplete review.

**Its threshold is derived from historical p95/p99 behaviour times a safety multiplier, and is not
set from one slice.** Until then the fuse is unarmed, and that is recorded rather than hidden.

---

## 11. WHAT MAY BE CLAIMED, AND WHEN

**No saving may be claimed until section 3's attribution exists.** Specifically withdrawn from
revision 1: the 20-50% estimates, and the ~20.5% figure that was used as a floor.

**The >=20% keep/revert threshold is withdrawn as a justification.** It was set from a derived
estimate and then used to judge that estimate. Permanent thresholds are set from **what makes this
extra complexity operationally worthwhile**, not from whatever number the first measurement produced.

**Until roughly ten real slices, or another defensibly sized sample, exist:**

- every threshold in this file is **provisional** and labelled so;
- no p50/p90/p95 is promoted to a rule;
- nothing terminates on any of them;
- the sample size is recorded beside every figure.

---

## 12. BASELINE IDENTITY - WHEN A MEASUREMENT STOPS APPLYING

**A baseline is segmented or invalidated when execution conditions change materially.** A change in
agent tooling can move token behaviour even when the model name is identical. Record, per row:

    model_served            reasoning effort
    reviewer/agent CLI version
    tool set / schema version, where exposed
    provider / API mode
    prompt-cache behaviour
    flow or kernel hash
    project instruction hash
    context-compaction behaviour, where observable

---

## 13. REVIEW QUALITY IS RECALL, NOT COUNT

**Revision 1's gate - "findings per round may not fall" - is withdrawn.** More findings do not mean a
better review, and that metric rewards noise.

**Build a fixed review-quality corpus** from defects this machine has already found, with the
artifact and the exact revision that contains each:

- the known production fail-open;
- the nine wrong implementations already discovered and killed;
- further historical defects as they accumulate;
- known-clean cases, where a false positive is the thing being measured.

**Track:**

| metric | rule |
|---|---|
| **critical-defect recall** | **must remain 100%** unless the operator changes that requirement |
| overall known-defect recall | must not regress |
| verified new findings | informational |
| false or unsupported findings | must not rise |
| review completion rate | must not worsen |

**A token-saving change that makes reviewers miss a known important defect is reverted, not
renegotiated.**

---

## 14. ECONOMICS, NAMED CORRECTLY

    tokens_per_successful_review = all attempted review tokens / fully successful rounds
    cost_per_successful_review   = all attempted review cost   / fully successful rounds
    quota_consumption_per_successful_review   (where quota is the binding constraint)

**Failed and incomplete attempts stay in the numerator.** They consumed the resource. A change that
lowers tokens while raising the INCOMPLETE rate is not cheaper, and this is the metric that says so.

In the baseline slice: **one round of four had all three families**. The other three cost full price
and bought two.

---

## 15. THE KERNEL EXPERIMENT

**Hypothesis, not a rule.** Section 2.3 measured ~12,627 tokens of stable context resent on every one
of 597 steps. Most of that is explanatory prose that a working agent re-reads hundreds of times.

Test a smaller always-loaded normative document - `FLOW-KERNEL.md` - carrying only the hard rules
needed continuously:

- step and state semantics;
- BLOCKED behaviour;
- the reviewer full-visibility rule;
- review independence;
- the re-review requirement;
- testing requirements;
- delivery requirements;
- this file's governing rules;
- **canonical absolute paths and content hashes for the full documents.**

The complete documents stay available by absolute path and nothing is removed from them:
`DELIVERY-FLOW.md`, `REVIEWING.md`, `TOKEN-BUDGET.md`.

**No information and no reviewer access is removed.** The only goal is to stop explanatory prose
being injected into every model turn. **Measure the saving - and the cost of any re-read the kernel
forces - before making it permanent.**

---

## 16. WHAT THIS MACHINE REFUSES

**A hard context cap on reviewer legs.** Section 5.

**Task-based model routing for reviewer legs.** A cheap-tier leg occupies its family's slot without
meeting its standard - a degraded leg recorded as a peer. Routing may apply to the implementer's own
subtasks; never to a leg. *(The uniform, recorded, output-confirmed step down to one level below each
leg's ceiling is an operator decision, not this.)*

**The FrugalGPT cascade, for reviewer legs.** A cascade needs a scorer that predicts whether an
answer is reliable. **A review's failure mode is a MISSING finding, and you cannot score the
confidence of an absence.** Measured here: round 4's family-C APPROVE with no defects was right;
round 2's family-B APPROVE with a surviving mutant in its own body was wrong. From outside the two
are the same shape. A cascade accepts both. Cascading is sound where the answer is checkable; it is
unsound where the product is the absence of a defect.

**Output discipline applied to a reviewer's findings.** Bound the brief and the prose, never the
evidence, the unresolved concerns or the completion record.

**Cartridges - out of scope**, trigger recorded: it optimises KV memory and throughput on
**self-hosted** inference, and this machine calls commercial APIs. Revisit only if self-hosting a
model against a large, slowly-changing corpus.

---

## 17. ACCEPTANCE CRITERIA

**Falling token consumption does not make this work successful.** It is successful only when
measurement shows all nine:

1. reviewer visibility unchanged;
2. review independence unchanged;
3. critical known-defect recall does not regress;
4. review INCOMPLETE rate does not worsen;
5. complete evidence remains available on disk;
6. token and cost attribution is good enough to **explain where a saving came from**;
7. token saving and cost saving reported **separately**;
8. no normal token budget silently terminates a valid reviewer;
9. every optimisation can be disabled and the previous behaviour restored.

---

## 18. IMPLEMENTATION ORDER

1. telemetry and token attribution (section 3);
2. real per-token-type cost accounting (section 4);
3. quota and availability preflight (section 6);
4. the known-defect / mutant quality corpus (section 13);
5. the I2 and I3 corrections (section 7);
6. evidence-access reporting (R4);
7. deterministic tool-output compaction (I4);
8. cache-effectiveness measurement (section 9);
9. the experimental compact kernel (section 15);
10. collect real data across multiple slices;
11. **only then** set permanent thresholds.

---

## 19. KILL SWITCH

Every rule in sections 7, 8 and 9 must be disableable by configuration alone, restoring full-history
behaviour **without editing any agent's code**:

    token_budget:
      compact_briefs:      true
      stateless_rounds:    true
      tool_output_cap:     true
      deterministic_compaction: true
      warn_thresholds:     true
      catastrophic_fuse:   false   # unarmed until section 10.2's data exists
      kernel:              false   # experimental, section 15

---

## 20. ONE PIECE OF EVIDENCE, STATED AT ITS REAL WEIGHT

A three-family design consultation was run under these rules - a bounded brief, a 900-word answer cap
- and cost **174,168 tokens**, producing three usable design answers and a correction to the author's
own arithmetic.

**That is evidence that compact briefs can preserve useful multi-model reasoning cheaply. It is not
evidence that a code review can be done for a fraction of its previous cost.** A design consultation
reads a brief; a code review reads a repository. They are not comparable, and revision 1's "4.0% of
one slice's reviews" invited exactly that comparison.

**The real saving from R1-R3 is unmeasured, and stays unmeasured until it is measured on real review
rounds.**
