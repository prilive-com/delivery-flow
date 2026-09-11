# delivery-flow

A mandatory 12-step delivery flow for AI-assisted software work, the tool-agnostic rules for running
independent multi-model reviewer legs, and the token budget that keeps the second one affordable.

| file | what it is |
|---|---|
| `DELIVERY-FLOW.md` | the flow: twelve steps, what each requires, and what counts as DONE |
| `REVIEWING.md` | how to run the reviewer legs steps 4 and 11 require |
| `TOKEN-BUDGET.md` | what a round of that review costs, and how to cut it without cutting the review |

In `DELIVERY-FLOW.md`, **I** and **me** are the person who adopts the flow; **you** is the agent
working for them.

## Using it

Point your agent's always-loaded instruction file at `DELIVERY-FLOW.md` — copy it, symlink it, or
import it, whichever your tool supports. Keep it as the canonical copy and edit it there; if your
tool needs the text inlined, generate that copy rather than editing it, and check the two still
match.

Load `REVIEWING.md` and `TOKEN-BUDGET.md` through that same instruction file. Without the first,
steps 4 and 11 have no rules to run on; without the second, they get expensive without anyone
noticing.

**Then write a third, local file that this repository deliberately does not contain**: which
reviewer tools you have, where they live, at what tier, and how each one fails. Name it whatever
your tool imports, load it the same way, and keep it local — it is wrong the moment someone else
pulls it.

The flow decides **whether** a step is required and **what counts as done**. Your project decides
**how it is spelled** — commands, paths, gates, integration branch. Where they conflict on a command
or a path, the project wins. Where the project would remove a step, the flow wins and the conflict
is a stop.

## What it is for

Ordinary engineering discipline, written down so an agent cannot skip it: every step ends in a
recorded state, every claim is VERIFIED or INFERRED, tests go red before they go green, every gate
category gets its own result, and a review that did not happen is never recorded as one that did.

Steps are not optional, a BLOCKED step stops the work, and a cap on review rounds ends the rounds
without converting an unreviewed fix into a reviewed one.

## On the token budget

It is here rather than in its own repository because its rules are rules *about this flow*. Its one
governing line — **cut what a brief repeats, never what a reviewer can see** — means nothing without
step 4 beside it, and two repositories would only recreate the problem the flow spends most of its
effort on: a fact fixed in one document and left stale in its twin.

It carries measured numbers from one real slice, not estimates — and **section 0 is where to start**,
because it is a list of what the previous revision got wrong. The first measurement the document
demanded falsified two of the document's own headline figures: a cache field had never been read, and
it turned out to be 93% of everything that ever entered the model.

Every saving claim has been withdrawn until the attribution in section 3 exists. A number here is
either measured, or marked `UNAVAILABLE`, or an estimate with its method written down. A zero that
means "we did not look" is the failure the whole section exists to prevent.

## Scope

These are instructions, not a framework. There is nothing to install and nothing to run.
