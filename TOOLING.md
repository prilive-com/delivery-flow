# TOOLING

The flow names no tools on purpose. It decides **whether** a step is required and
**what counts as done**; the project decides **how it is spelled**. That keeps it
usable on a machine that has none of what this file lists.

But a reader of step 3 hits *"documentation tooling"* and a reader of step 12 hits
*"the browser-driving tooling the profile names"*, and if nothing tells them what
those are, the step points at nothing. **This file is that list.** It is the
reference, not the profile: your own step 1 records which of these you actually
have, how each is invoked here, and what to do when one is missing.

**This file names products; the flow never does.** That is the split, not an
inconsistency: the flow must stay usable on a machine with none of these, so it names
the CAPABILITY and leaves the instance to the profile. This file is the instance list -
one rung more concrete than the flow, one rung less specific than your profile, which
records versions, invocations and what is actually installed.

Nothing below is required for the flow to work. Each entry says which step wants it
and what you lose without it.

---

## Documentation lookup — step 3

**context7 MCP server.** Resolves a library to an identifier, then returns its
documentation.

Step 3 splits sources by what each establishes, and this tool sits on one side of
that split:

> **Documentation tooling DISCOVERS; it does not CONFIRM.**

Use it freely and early — to find what exists, what a thing is called, the shape of
an API, the idiom. There is no budget for asking. But a claim resting only on it is
**INFERRED**, even when you asked for a version, because it does not reliably scope
its answer to the version you named. To reach **VERIFIED**, confirm the one fact you
are about to encode against a version-exact source: the toolchain pinned to the
version the project declares, the locked source your build compiles, or the upstream
page for that version.

**Without it:** step 3 still applies. Read the locked source your build compiles,
or the upstream page. You lose speed, not correctness.

## Browser proof — step 12

**Playwright MCP server.** Drives a real browser.

Step 12 requires a change to be proven outside the test suite, and names the exit
condition per kind of change. For a user interface the exit condition is that the
interface was exercised in a browser — **front end and back end both**. A passing
component test is not that proof.

**Without it:** the block is on the missing PROOF, not on this product. Any tool that
drives a real browser satisfies step 12; if none is available, the UI slice cannot reach
its exit condition and that is BLOCKED. What is never acceptable is substituting a
weaker proof - a passing component test - and calling the step done.

## Complexity and duplication reports — steps 2, 9 and 10

The design questions in step 2 and this trial take selected ideas from
[ub-mode](https://github.com/unclebob/ub-mode/blob/57a8bdd28e45ed41900ace0bafa2ff76dd9ed70f/SKILL.md),
inspected on 2026-10-27. The delivery flow remains the authority for tests,
review, scope and MR delivery. This adopts a checklist and a trial protocol;
it does not install or activate the upstream skill or tools.

**Start with one project.** Run the trial as a named, authorized project slice.
Step 6's scope and RELEASE CANDIDATE FIRST rules still apply.
Check its existing tools first. Use a small representative area and compare a
known baseline with the final source. Include relevant existing code when looking
for new duplicates, so copying an old function into a new file is visible.
Record the language, supported paths, exclusions and any code the tool cannot see.
An unsupported area is unmeasured, never a clean result.

Before running, record the chosen tool's exact version or commit under step 3,
its commands, the source/coverage revision, the report paths and numeric limits
for time, memory, workers and temporary disk use. Respect the project's existing
container and resource rules. Use task-owned working space away from another
agent's active tree. Check install side effects and dependencies first; selecting
a trial does not grant permission to change shared tools or project dependencies.
Both metric tools write `.metrics` reports; confine those writes to task-owned space.

Check that the report detects a known complex function and a known duplicate
pair. Keep those control inputs and outputs as evidence. Record the measured
scores beside any proposed thresholds and their exact comparators. Review each
candidate before changing code: similar structure can express different rules,
and a lower score alone does not prove better behavior. Keep tests for behavior.

The trial report records useful findings, false warnings, changes made, elapsed
time, peak memory and temporary disk use, with commands and evidence. Mark a
measurement UNAVAILABLE when it was not captured. Retain the source identities,
coverage inputs and full reports, then use step 12's ownership/current-use checks
to remove only the trial's disposable resources. Recommend adopt, adjust or drop
from those results. Making a tool or threshold a required project gate is an
explicit owner decision recorded in the project profile; this protocol alone
does not make it required. Existing gates keep their rules.

Companion tools are candidates, not a required bundle. These are source-review
findings for the linked revisions, not proof that they run in a given project:

- [crapper](https://github.com/unclebob/crapper/blob/6fd92c4c9bcc56efb64a2f8743d5a2993bcfd42d/README.md)
  combines function complexity with test coverage. Without a threshold, a high
  score does not fail the command. Its threshold comparison is strictly `>`:
  a threshold of 10 accepts 10, whereas the upstream skill asks for `< 10`.
  Use current coverage from the measured source. A missing or failed coverage
  run must be recorded separately; a metric report is not proof that tests ran.
  The tool scores missing or failed coverage as 0% and still writes the report.
  Check the coverage command's own result before relying on the scores.
  With coverage disabled, CRAP is unavailable and its threshold cannot fire.
  Default coverage runs execute tests, remove old reports and can install
  packages or tools. Check existing-coverage or custom-coverage options first.
  Confine report writes and installs to task-owned space, and inspect ignored
  and untracked files as well as manifest changes after a run.
- [dryer](https://github.com/unclebob/dryer/blob/66ff6d21a42c04afcad89c78a80066176d1294b0/README.md)
  reports structural similarity. Its default is 0.82, while the skill calls for
  acting at 0.8. A successful report exits 0 even with duplicate candidates.
  Read the findings; exit 0 does not mean no duplicates. Do not force unrelated
  code into one abstraction to meet a number.
- [mutator](https://github.com/unclebob/mutator/blob/a5a0cb803b66e0cdb8bf471b3b08af701d424a41/README.md)
  is a separate option for mutation testing. Its inspected version counts
  compilation failures and timeouts as kills, and caches kills for unchanged
  function text. Those results alone do not meet step 10's mutation rules,
  including test changes, full final runs and valid kills. Any later use needs
  its own project validation. The complexity/duplication trial does not add it.
  It also skips uncovered sites, defaults to one worker per core and can restore
  an interrupted older run's backup into the real tree before a new run.

All three inspected tools list Clojure, Java, Go, TypeScript, Rust and Python
support. Only crapper and mutator also list JavaScript; that dryer revision does
not discover JavaScript files. None lists PHP support. Check the chosen version's
actual support and run controls before relying on it, including for Laravel
projects.

**Without them:** keep the existing gates and design review. An unadopted
advisory trial is not a missing required capability and does not block delivery.

## Reviewers — steps 4 and 11

**Reviewers are the one capability whose instances are NOT listed here.** A documentation
or browser tool is the same product everywhere; a reviewer roster is a property of one
machine's accounts and quotas, so it belongs in the profile and changes without notice.
What is portable is the shape:

**One leg per model family.** A second from a family already represented is one
opinion counted twice, so the count that matters is families, not processes. A leg need
not be a CLI - one may be in-process, or a tool your harness already provides.

Your profile records the following. **Name that profile's path in your project's
instruction file**, so a leg handed only this document can still find it - this file is the
capability list, never the machine's answers:

- which families are **PRIMARY**, and how many legs a round runs;
- which is the **SUBSTITUTE** — it replaces an absent primary and never adds an
  extra opinion;
- the **invocation** for each, including the flag that stops its tools being
  auto-denied;
- the **validity gate** for each — what proves a leg actually reviewed something;
- the **probe** for each - free surface first; step 4 permits a minimal paid probe only
  where no free one can establish the seat, and requires the record to separate
  REACHABLE from CAN RETURN A REVIEW.

Three things are worth knowing before you build that list, because each has cost a
real round:

**A clean exit code proves nothing.** Every CLI here has at least one failure mode
that exits 0 with an empty or absent result: tools auto-denied, a dead
authentication tier, a content filter replacing the answer. Gate each leg on its own
evidence — a non-empty output file, a success status, a terminal stop reason — never
on `rc` alone.

**No leg is read-only.** Assume every one can write to your tree until you have
tested otherwise. The brief's do-not-modify instruction only ASKS. **Nothing you can
set up in the repository PREVENTS.** So check afterwards, and know what the check
misses.

Compare the file CONTENTS before and after. Hashing `git status --porcelain` is the
obvious check and it is too weak: it shows only that a file is dirty, not how many
times it changed, so a second edit to an already-dirty file gives the same hash - and
mid-slice your tree is usually already dirty. Even a content comparison finds only the
differences that REMAIN, so an edit that was undone before you looked leaves nothing
to see.

**Do not assume a leg loads the flow by itself.** Some do and some do not, and the
difference is per-tool. Name the flow's own path in the brief either way: it costs
nothing, and pointing at a file that points at the flow is a hop a leg will skip.

**Without them:** the flow degrades rather than stops. Report the missing leg, its
family and the reason, and continue with what is left. The floor is one.

---

## What step 1 records

Not a copy of this file. The answers for **your** machine:

| question | why the flow needs it |
|---|---|
| Which of these exist here, and at what version? | Step 1 forbids assuming a capability |
| The exact invocation of each | A brief that names a tool a leg cannot call produces a fabricated capability report |
| The validity gate for each reviewer | Otherwise a failed leg is recorded as a peer |
| The probe for each reviewer, and what it does and does not establish | Step 4 re-probes every absent leg at the start of a new slice |
| Which families are primary, which substitutes | Step 4 uses the seats your profile assigns |
| What is missing, and what that costs | An absence is a finding, not a silence |

**Record the asymmetry.** These tools are not interchangeable. Each fails in a
characteristic way, and knowing which predicts which kind of defect each will miss.
