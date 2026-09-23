# INDEPENDENT REVIEW LEGS

How to run the reviewer legs that steps 4 and 11 of `DELIVERY-FLOW.md` require. A **leg** is one
independent reviewer run: one model family. A **round** is one launch of every leg against the
same frozen artifact.

No tool, path, model or vendor is named here. Keep that list on your own machine; this file is the
part that does not change.

## Composition

**One leg per model family. A second leg from a family already represented is one opinion counted
twice.** The machine profile names how many legs a round runs and the order in which families fill
the seats - for example two legs: the author's own family always, plus the first family in an
ordered list whose probe passes. A substitute only replaces a missing leg; it never adds an opinion.

**Use the newest model each family offers, and where the tool has a reasoning-effort setting, at
an effort you have decided and written down.** Resolve both at run time rather than pinning a name.
Confirm from the tool's own output which model answered, and at which effort — never from the flag
you passed.

**Never put legs in conversation with each other.** Within a round, no leg sees another's output.
Across rounds the corrections travel; that is re-review, not debate.

## What every leg needs

- **Full access and full context.** Code, plan, test plan, review history, the project's own
  instruction and rule files, and your specific questions. Never narrow what a reviewer can see —
  including when a reviewer suggests it.
- **Absolute paths to the governing documents, not pointers to them.** Never rely on a leg
  following a second hop: naming a file that names your flow is not naming your flow.
- **The freeze identity, with an instruction to report a mismatch.** Baseline, head commit, diff
  hash, and the command that reproduces it.
- **"Mark every claim VERIFIED or INFERRED, with command output or `file:line`."** Without it you
  get confident prose instead of evidence.
- **"Say which rule or file each finding rests on."** Converts taste into something checkable, and
  exposes a leg inventing a standard your project does not hold.
- **A "known and deliberate — do not report unless you think it is wrong" section.** Listing the
  intentional red gates and accepted trade-offs buys back a round of noise, and invites disagreement
  exactly where you are least sure.
- **"If you find nothing in a category, say so rather than padding."** Padding is indistinguishable
  from a weak finding at synthesis time.
- **An explicit do-not-modify instruction, and your own mechanical check.** Assume no leg is
  read-only until you have tested that specific tool in that specific mode. Compare a hash of the
  working-tree status before and after.
- **A control question only your project's rules can answer.** A leg reviewing without your
  standards is a degraded leg you will otherwise record as a peer.

## Isolation must be structural

**Any artifact a round asks every reviewer to WRITE to is one they can READ from.** A single shared
findings file, given to concurrently running legs, destroys blindness: the first to write becomes
readable by the rest. The failure is invisible — reading another leg's notes makes a review look
*better*, so no output shows it and no gate catches it.

One file per family, named by family, addressed by **absolute path**, plus a brief line forbidding a
leg to read any other. A leg's working directory is rarely what you assume.

## A leg counts only if it actually ran

**Exit code is not evidence.** A tool can report success having done nothing. Each of these
does:

- tools auto-denied because a permission flag was missing → success status, empty review;
- an authentication or entitlement failure the tool reports as a normal completion;
- a prompt delivered in a form the tool did not accept, answered literally;
- an internal timeout the tool reports as its own clean result;
- a content filter that replaces the final answer while the whole transcript looks like work.

**So gate every leg on all of: process exit; the tool's own completion status, where it reports one;
a non-empty response; and the served model matching the one you resolved.** All of them, or the leg
did not happen. A tool that reports no status of its own leaves you one signal short — record that
with the round.

**A single command-line argument can be capped far below the whole command line.** Deliver
a large brief on standard input, or write it to a file and pass a short pointer — then verify the
leg quotes something from it back.

## When a leg fails

Restart it. If it fails again, try another interface in the same family, then the family the profile
names as the substitute. If it still will not run, **report the leg, its family and the reason at
once, and continue the round with the legs that remain.** That is a recorded degradation, never a
silent one and never a stop: every artifact carrying the round's verdict says how many legs ran and
which were missing. **The floor is one leg**; zero is a stop. A one-leg round that shares the author's
family is the weakest review this flow can produce, and says so. Record the failure with its
evidence, so a later reader can judge whether the round can be trusted. An unavailable leg is a
state, not a verdict: probe it again at the start of the next slice.

A refusal is not always about your repository: the same leg may refuse a brief phrased as *build a
working bypass* and answer the same substance phrased as *name the limits of this check*. Reword in
a new round; never silently rerun.

## Reading the round

How findings are weighed is in `DELIVERY-FLOW.md` steps 4 and 5. Two things it does not say:

- **When findings stop landing in the code and start landing only in the prose, that is a signal
  about artifact size, not reviewer quality.** Shrink the document rather than buying another round.
- **Legs are not interchangeable.** Each fails in a characteristic way. Record the asymmetry with
  every round: it predicts which leg will miss which kind of defect.

## Briefs that get more back

- Ask for **what is missing** and **what this contradicts**, not only what is wrong.
- Ask a leg to **report its own tool schema first**, rather than instructing it to use tools it may
  not have. An instruction to use a tool invites a fabricated capability report.
- Tell a leg to **execute rather than reason** wherever a check is runnable, and require scratch work
  to live outside the repository.
- Where a proof is a test, ask a leg to **build a wrong implementation that the test still passes**.
