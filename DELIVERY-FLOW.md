# THE DELIVERY FLOW: MANDATORY, NOT ADVISORY

Applies to every implementation, fix, refactor, pipeline change and deployment, in every project and language. You may not skip, reorder or compress a step. The state table is the only way a step is excused - except under `dsf`, at the end of this flow, which says when it is on and which steps it drops.

This flow decides WHETHER a step is required and WHAT COUNTS AS DONE. The project decides HOW IT IS SPELLED: commands, paths, gates, integration branch, backlog. Read its instruction files first. On a command or a path, the project wins. If one would remove a step, this flow wins and that conflict is a stop. If the project does not answer such a question, find the answer once and write it there.

Split the work into slices: one scope each, independently testable and revertible. Never mix a refactor, a dependency upgrade and a behaviour change. One scope per document too. Finish one slice before starting the next.

Every step ends in one recorded state. Record them as a table: step, state, artifact, one line of evidence, no gaps. The state is a lookup, not a judgement:

```
  the surface or gate does not exist here -> NOT TRIGGERED, with the evidence it does not apply
  it applies and the capability exists    -> run it; PASS only on its documented success criterion
  a tool, environment,
    credential or permission is missing   -> BLOCKED
  a REVIEWER leg is missing               -> not BLOCKED: report it, continue on the
                                             legs that remain, record the degradation
                                             (step 4). Zero legs IS blocked. THIS ROW
                                             WINS over the one above it whenever the
                                             thing missing is a reviewer leg - including
                                             when the proximate cause is that leg's own
                                             credential, quota, licence or tool, which
                                             is what it usually is.
  the technique is unavailable but its
    evidence goal has a substitute        -> use the substitute and record it
  the tool misses an affected part        -> run extra scoped checks, or BLOCKED
  the gate already fails at the baseline  -> reproduce on baseline AND on the final state, then
                                             classify; never silently call it PASS
```

BLOCKED NEVER ADVANCES: no later step, commit, deployment or next slice until it is resolved or I change the task. A step that leaves no artifact will be faked, so each names what must exist when it is done.

Redact credential VALUES and nothing else: keep the file, code path, field names and error shape. Never show a reviewer less. If a credential reaches an artifact, mark the step BLOCKED, stop publication, name the artifact without repeating the value, and tell me to rotate it.

Process artifacts are not product. Keep plans, briefs, reviewer output and registers where the project does not track them. What you track is the finished result: the frozen plan and the facts, never the history that produced them.

`TOOLING.md` beside this file lists the tool CAPABILITIES these steps assume - documentation lookup, browser proof, reviewer legs - and what each step loses without one. It names no machine; your step 1 records which of them exist here.

**1. DISCOVER THE PROJECT.** Record a profile, citing each entry's source: instruction files and their precedence; repository and module boundaries; the revision or a reproducible snapshot identity; manifests, lockfiles, pinned toolchains; every gate the project actually has; available reviewers; deployment and rollback capability AND your permissions for each; where plans, evidence, review history and future work live, and which are tracked. Never invent a gate or assume a capability.

**2. PLAN.** Research the best current approach, then write the plan where the profile says. It records: baseline identity, the problem, acceptance criteria, non-goals, the code you actually read, the search and nearest match for every new name, affected components, proposed behaviour, the test strategy and its red command, external-contract evidence, the applicable gates, and how you will deliver and recover. Every claim about current state cites a file, a command result or a source. No detailed spec for a one-line fix.

**3. LOOK UP WHAT YOU ARE ABOUT TO ENCODE.** Before writing any external claim into code, a test, a plan, a review or a commit message, look it up: an external service's contract, a third-party API you depend on, any tool behaviour not settled by its help output or a run. "I already know this" is never an exemption. Rank sources by what each establishes.

A run establishes what THIS BUILD does. Run anything executable in the tree; record version, environment, command, result. It outranks documentation and every reviewer about the machine you are on, never about a remote service. For a pinned dependency, read the locked source your build compiles.

A specification establishes what is GUARANTEED. Where the two disagree, the run wins on behaviour, the specification on guarantees, and code depending on the difference stays INFERRED.

Documentation tooling DISCOVERS; it does not CONFIRM. Use it freely and early, for any language, to find what exists, what a thing is called, the shape of an API, the idiom. A claim resting only on it is INFERRED even when you asked for a version, because such tooling does not reliably scope its answer to the version you named. To reach VERIFIED, confirm the one fact you are encoding against a version-exact source.

If a lookup misses the exact thing, record NOT INDEXED and go upstream: a wrong answer with a citation is worse than an honest INFERRED. Mark every VERIFIED claim with source, version or date, and passage. Where documentation specifies no wording, ordering or guarantee, that silence IS the finding. Re-run this whenever later work introduces a new external claim.

**4. REVIEW THE PLAN.** Freeze the artifact and record its identity. THE FREEZE BINDS YOU: check it yourself before launching, then hold every finding, yours and theirs, until the round closes. Give each reviewer the hash it should see and ask it to report a mismatch.

Use independent reviewers, ONE PER MODEL FAMILY: a second from a family already represented is one opinion counted twice. The profile names which families are PRIMARY and which SUBSTITUTE for a missing one, and how many legs a round runs; a substitute is used only to replace an absent primary, never to add an opinion beyond the number of primaries the profile calls for. Use the newest model each offers, and where the tool has a reasoning-effort setting, at an effort you have decided and written down; resolve both at run time rather than pinning a name, then confirm from the tool's own output which model answered, and at which effort where it reports one. Give each full context, full access and your specific questions. NEVER narrow what a reviewer can see, even if a reviewer suggests it. Confirm each has what you think, with a control question only the project's rules can answer. They are not equally equipped, so record the asymmetry. Assume none is read-only until tested. Ask for the most native, minimal solution that fully does the job, and for a deep review of what you missed. Launch them against the same frozen brief before saving any output; within a round no reviewer sees another's.

DONE when each raw output is saved verbatim to its own file, headed with revision, date, baseline, each reviewer's model and verdict, and any degraded reviewer. A reviewer counts only if it exited cleanly, returned findings or an explicit no-findings verdict, and named the revision it reviewed; an exit code alone does not establish that. If one fails, restart it; if it fails again, try another interface in the same family, then the substitute the profile names. IF IT STILL WILL NOT RUN, TELL ME AT ONCE - naming the leg, its family and the reason - AND CONTINUE THE ROUND WITH THE LEGS THAT REMAIN. A leg that cannot run is a RECORDED DEGRADATION, not a BLOCKED step: it does not stop the slice, and it is never silent. Every artifact carrying that round's verdict states how many legs ran, which were missing, and why - a round run short is never described as a full one. THE FLOOR IS ONE: a round with no leg at all cannot happen and is a stop. A one-leg round states that it was one, and whether that leg SHARES A FAMILY WITH THE AGENT THAT WROTE THE CHANGE - which is the weakest review this flow can produce, because none of the comparison this step is built on happens at all. A LEG RECORDED UNAVAILABLE IS RE-PROBED AT THE START OF EVERY NEW SLICE, before the round is planned: availability is a STATE, not a verdict, and a leg written off from an error string stays written off long after it recovered. Probe on a free surface first - a catalogue or login call. Where no free surface can establish the seat, a MINIMAL probe that spends the least the tool allows is permitted; a review is never a probe. Two different things count as alive and the record names which: the interface is REACHABLE, and the family can RETURN A VALID REVIEW. Where a free probe establishes only the first, record the second as unknown rather than as alive. Record what the probe returned, not what the last failure said. An automatic or on-edit reviewer never substitutes for one: judge its findings, never count it, and a tool scoped to part of the tree says nothing about what it cannot see.

Reviewers are deliberately NOT in conversation. Convergence is agreement, not correctness, and a finding with one author is not weaker for being alone. When two contradict each other on a fact, ask the code: run the command, read the line, write down what it says.

**5. SYNTHESISE.** Take the strongest argument, not the majority, and verify contested claims yourself. DONE when a register records every finding as ACCEPT, REJECT or DEFER with evidence. A REJECT needs a citation, command or source, and so does an ACCEPT that changes the design. Never require unanimity. A DEFER does not survive the slice: close it with evidence or write it to the backlog with its trigger. Disagreements evidence cannot settle are MINE: if a dispute turns on a preference between two designs that both satisfy the constraints, stop and put both to me.

RE-REVIEW. A materially changed artifact is a new revision and goes back through review, including changes made because of a review. Scope it to the delta and its blast radius, same reviewers - meaning the seats the profile calls for, re-probed, not merely the subset that happened to run last time. Fix the cap on rounds before starting, the same for every artifact type: **five, unless I say otherwise.** Fewer needs my agreement and a reason recorded, because a cap is a budget for finding defects and I would rather spend it than ship past it. THE CAP ENDS THE ROUNDS; IT NEVER CONVERTS AN UNREVIEWED FIX INTO A REVIEWED ONE. If the cap falls due with a correction no reviewer has seen, the slice stops and comes to me with that correction named. If findings keep coming past the cap, stop and tell me: that is a signal about the artifact.

**PRODUCT CONVERGENCE ENDS THE ROUNDS. Owner decision, 2026-09-20.** Count findings in the **TRACKED CHANGE SET** only. **Two consecutive rounds with zero findings there and the slice SHIPS**, even if reviewers are still finding things in your process artifacts.

Findings in gitignored process artifacts - checkers, freeze scripts, launchers, briefs, plans, gate records - are REAL, and you fix them. **They go to the backlog with a trigger. They never restart the cap, and they are never a reason to open another round.** Nobody ships them.

**This does NOT narrow what a reviewer can see, and it must never be used to.** Legs keep full access to everything, including your tooling, and they SHOULD read it: measured on one slice, three of the most valuable findings of the whole review came from legs reading exactly those files - a fabricated search recorded as evidence, a gate record describing a different revision than the one frozen, and a proof that passed a false document. What changes is only which findings restart the budget.

**THE MEASUREMENT THAT PRODUCED THIS RULE, so it can be checked rather than believed.** One slice, five rounds: the tracked change set went 98 -> 136 -> 150 -> 163 -> 164 insertions, so the last round moved ONE line of product, while the proof was rewritten seven times and one check inside it five times, each version defeated by a reviewer. All legs had said "ship the documents" two rounds earlier. **The findings had stopped landing in the product and started landing in the proof**, which `REVIEWING.md` already names as a signal about the artifact rather than about reviewer quality - this rule is what acts on that signal.

**The failure mode this prevents is LOOPING, not stopping,** and it is self-feeding: on that slice almost every finding in rounds 2 to 4 was in a correction the agent had just made. A higher cap buys more rounds of the same. If findings keep coming in the PRODUCT past the cap, that is the different signal the paragraph below is about, and it still stops.

**6. NO OVERENGINEERING**, from you or a reviewer. Solve exactly the task that exists. Write good extensions to the backlog with their trigger, or to the handoff if there is none. If measurement shows the change is not worth making at all, that is a stop, not your decision.

Every NEW name - symbol, field, file, table, dependency, package - is a claim that nothing here already carries this. Record the exact search you ran and the nearest thing it found, in the plan, where the reviewers see it before the code exists. Untidy is not unfit; incorrect is.

**7. TEST PLAN: its own document, its own review round**, permanently separate from the plan. A design review asks whether the change is right; a test review asks whether the proof would catch it being wrong. Merging them lets whoever decided the first answer the second.

**8. TESTS FIRST, WITH THE RED RECORDED.** Write the tests and run them. DONE when you have the exact command, exit code, verbatim failing output, and one line saying why the failure is the missing behaviour and not a compile error or a bad fixture. A test that passes before the implementation exists is not a test of this change: find out why first. Anything touching timing, concurrency or shared state runs under the toolchain's race or hazard detector, repeated enough to trust; if there is none, say so and name what you ran instead. Never weaken, skip or delete a test to get green.

**9. IMPLEMENT** the minimum reviewed design. If it needs an unplanned file, symbol, dependency, config field or behaviour: stop, amend the plan and test strategy, redo the affected lookups, re-review. DONE when the change matches the recorded scope, or every deviation has a disposition. Then make one pass whose only goal is finding code this slice added that should be deleted, inlined or replaced with reuse. Reviewers are the last to notice absence.

**10. GATES BEFORE EYES.** Run every category the project HAS: format; the full test suite; the concurrency detector; type and static analysis; the linter; dependency vulnerability and provenance; dead code; and a production build of EVERY CONFIGURATION THAT SHIPS. Each gets its OWN state; never bundle them into one result that can be neither honestly PASS nor honestly NOT TRIGGERED. Pin the toolchain to the version the project declares: a result from a newer one is not evidence about a project targeting an older one. Where a category has no runnable command, that absence is itself a finding: record the ad-hoc command and its output, and never report a category as covered by a target that does not exist. DONE when commands, versions, exit codes and output are recorded. "It passed for me" is not a result.

**A REPORT OF SUCCESS IS NOT EVIDENCE OF SUCCESS. RE-READ THE ARTIFACT.** Your own script saying it applied a fix, your own generator printing a gate record, your own harness reporting a pass - none of those is the thing itself. **Measured FIVE times in one slice:** a `printf` placeholder sat where an exit code should have been; a patch script wrote the file before two later edits ran and printed both as applied; a falsification test reported the attack still passing because the patcher had a missing argument and had patched nothing; another patcher wrote literal newlines and left the checker unparseable; and a gate record was generated before the change was staged, so it described the previous revision. Every one was caught the same way - by running the thing and reading the file - and not one was caught by the message the tool printed.

This applies to DOCUMENTS too: before an artifact reaches a reviewer, resolve every file and line citation and fail on a blank line or missing file, resolve every named symbol and path, and never assert a count beside one that can be computed.

**11. REVIEW THE CHANGE**, same rules as step 4. Freeze the complete change set INCLUDING FILES NOT YET TRACKED and review against exactly that. Ask for unnecessary code and overloaded implementation. Look up any reviewer claim about an external contract, exactly like your own. Fix what is genuinely wrong and re-review under the same cap: a fix that never went back through review is unreviewed. Then run all the tests. If you cannot finish a test, that is BLOCKED: write the message for whoever picks it up and stop. It is not permission to commit or deploy.

**12. DELIVER, THEN PROVE IT.** Commit and push through a merge or pull request: focused commits on a branch, onto the integration branch, never pushed to it directly. Verify the tree contains only this slice and that every new file was in the review scope. A disabled or absent pipeline is not a green pipeline: the step-10 record is then the only evidence, so put commands, versions and exit codes in the request itself and never call it CI-green.

Then deploy and prove it works outside the test suite. Confirm first that what is running is what you think is running. Name which exit condition applies: a behaviour change is exercised on the environment against the behaviour you changed, with the evidence pasted; where the only real proof is an action with an external side effect, perform that action for real; a build or packaging change runs the new command in every configuration that ships; a user interface is exercised through the browser-driving tooling the profile names, front end and back end both; a docs-only change records "docs only, no runtime surface", which is the exit condition, not a skip. Define the rollback first and check it is SYMMETRIC. If verification fails, roll back or fix forward before the next slice, and a fix-forward re-enters at step 9. Without deployment authority, finish as READY_FOR_DEPLOYMENT with exact deploy, smoke-test and rollback instructions, and stop.

CLEAR CONTEXT AFTER EACH SLICE. First write a handoff naming the finished slice, the baseline identity, the PATHS of the review outputs, the validation results, the deployment state, EVERY SLICE STILL OUTSTANDING IN ORDER, and the exact next step. The boundary is a pause, not a stop.

**FINISHING A SLICE IS NOT A REASON TO STOP. Owner instruction, 2026-09-20.** A merged MR, a green gate record, a closed review round, a written handoff and a cleared context are all the MIDDLE of the work. When a slice ends and nothing is blocked, the next action is to START THE NEXT SLICE IN THE SAME TURN - look it up, do not decide it: the profile names where the queue lives, and its top entry carries the literal command. Report what landed and take that next step in one message. **A message that ends with a finished slice and no tool call has stopped, and stopping there is the defect this paragraph exists to prevent.** It has happened repeatedly, and every time it looked like diligence rather than like quitting.

DON'T STOP UNTIL THE IMPLEMENTATION IS FINISHED. **THERE IS EXACTLY ONE REASON TO STOP: A REAL BLOCKER, AND THE LIST IN THIS PARAGRAPH IS THAT LIST.** Nothing outside it is a stop, however natural a pause it feels like. Going back a step to amend and re-review is not stopping. Finishing a slice is not stopping. Neither is a merged MR, a closed review round, a green pipeline, a handoff, a cleared context, or running out of things that felt urgent. A stop is when you need me: a credential only I hold; a decision only I can make, including whether a slice I asked for should not be built; a permission you were denied; a review gate that needs my reply; an escalation asking for my choice, which you forward verbatim; a round with NO reviewer leg left at all - a single missing leg is reported and continued past, never stopped on; the cap falling due on an unreviewed correction; a required test you cannot finish; no deployment authority; a credential exposed in an artifact; or a disagreement evidence cannot settle. Any step recorded BLOCKED is one of these. Say what is blocked, the last reviewed identity, and the exact action you need from me.

**AUTO-DECIDE AFTER ONE HOUR. Owner instruction, 2026-09-14, verbatim:** *"if i am not reat on your
questions like this one hour or more - chhose automatically option that you reccomend"*.

**When you have put a CLOSED SET OF OPTIONS to me with a named recommendation, and one hour has passed
with no message from me, take your own recommendation and continue.** Record it as an AUTO-DECISION
with the hour it fell due, so I can see what was chosen for me and reverse it.

**This narrows the stop list above. It does not delete it. It DOES NOT APPLY to:**

- anything OUTWARD-FACING or hard to reverse — deploying, pushing to the integration branch, deleting,
  rotating, publishing, or any action with an external side effect;
- a credential exposed in an artifact, or a credential or permission only I can supply;
- whether a slice should be built AT ALL, or any change to what we are building;
- an option you would refuse to carry out — **if you would not do one of the options, you may not
  auto-pick another; say so and keep waiting**;
- any question where you did NOT name a recommendation. **Do not invent one after the hour to unlock
  yourself.**

**The hour runs from your message, not from a heartbeat.** A heartbeat is still not consent — it marks
the time passing, and this rule is what converts elapsed time into permission, for this narrow class
only.

**THE EVIDENCE THAT THIS WILL SOMETIMES BE WRONG, recorded at the moment it was written.** The message
that asked for this rule also answered the pending question — **with a different option than the one
recommended.** Had the rule been in force an hour earlier it would have chosen C, and the owner chose
B. **So an auto-decision is a real transfer of judgement, not a formality. Mark them clearly and keep
them cheap to reverse.**

**`dsf` — DO THE SIMPLER FLOW. Owner instruction, 2026-09-23, verbatim:** *"Can we add an alias in our
main developing flow - dsf - do the simpler flow - it`s mean that if I write it in task flow should be
simpler - only one final review and only final tests"*.

**When it is on.** When I write `dsf` in a task. When a project's queue or backlog marks an item for "a
simpler flow" on my order. **And ALWAYS for a docs-only change.** Owner, 2026-09-23, verbatim: *"can you
add that for documentations, instructions we always should use dsf"*. A change is docs-only when it changes
only prose: documentation, READMEs, instruction and rule files, plans, registers, queues, and comments. It is
NOT docs-only if it changes code, tests, configuration (permission settings, CI and build files included),
or an example that a test or an operator runs as it is, such as a config block or a command. If a docs-only
slice turns out to need such a change, it leaves `dsf` for the full flow, unless I wrote `dsf`. Nothing else
turns `dsf` on: you never choose it for yourself. Record which of these turned it on, in the plan and in the
MR.

**What `dsf` drops - and nothing else:**

- the plan review rounds (steps 4-5 for the plan). Write a short plan instead (step 2): the problem, the
  change, the files, and step 6's search and nearest match for every new name. The final review reads it;
- the separate test plan and its review round (step 7);
- tests FIRST and the recorded red (the order in step 8). Write the tests with the change. Step 8's other
  rules stay: never weaken, skip or delete a test to get green, and run anything that touches timing,
  concurrency or shared state under the race detector, repeated;
- every review before the final one, and every review after it: the RE-REVIEW rule, its cap, the two clean
  rounds of PRODUCT CONVERGENCE, and step 9's "re-review" of an unplanned change (add it to the short plan
  instead). So a fix made after the one review round is not the stop "the cap falling due on an unreviewed
  correction";
- a project's own rule that requires one of these steps, such as a recorded red.

**What `dsf` keeps: everything else, unchanged.** In particular:

- **the final tests:** every gate the project has (step 10), on the final change set. Run them before the
  review, and again after any fix;
- **ONE final review round** (step 11) on the final change set, frozen, with the reviewer legs step 4
  calls for. Ask it both questions: is the change right, and would its tests catch it being wrong? Every
  finding still gets ACCEPT, REJECT or DEFER with evidence, as step 5 says. Fix what is really wrong. The
  fixes are not reviewed again: the MR lists each one as "fixed after the review, not re-reviewed",
  together with any file such a fix adds;
- delivery (step 12) and its proof.

**`dsf` is less process, not less honesty.** A dropped step is recorded as "dsf: not run", never as PASS.
