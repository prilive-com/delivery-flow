# THE DELIVERY FLOW: MANDATORY, NOT ADVISORY

Applies to every implementation, fix, refactor, pipeline change and deployment, in every project and language. You may not skip, reorder or compress a step. The state table is the only way a step is excused, except for the selected mode below. `dmf` (do medium flow) is the default; `dsf` and full flow remain available. FLOW SELECTION and the mode rules at the end decide which reviews apply.

This flow decides WHETHER a step is required and WHAT COUNTS AS DONE. The project decides HOW IT IS SPELLED: commands, paths, gates, integration branch, backlog. Read its instruction files first. On a command or a path, the project wins. If one would remove a step, this flow wins and that conflict is a stop. If the project does not answer such a question, find the answer once and write it there.

Split the work into slices: one scope each, independently testable and revertible. Never mix a refactor, a dependency upgrade and a behaviour change. One scope per document too. Finish one slice before starting the next.

**MR SIZE: RELATED TESTS HAVE THEIR OWN BUDGET. Owner decision, 2026-09-29, verbatim:** *"Ok, let`s increase in main flow for related tests mr up to 1200 lines"*, then *"Hm, let`s increase to 2000"*. Where a project's size rule counts tests, count an MR's changed lines (added plus deleted) in two budgets. Related tests - the test files and test data that exercise this MR's change - may take up to 2,000 lines; above that, split. In an MR with no production code, its tests are its change, so they are related tests. Everything else - production code, scripts, configuration, documents, and a test helper that no test in this MR uses - keeps the project's own size rule. The project's exceptions (generated code, mechanical renames and the like) apply to both budgets. Record both counts in the MR. The measurement behind it is small (one project's merge history, 2026-09-29: size predicted more review rounds, not more escapes), so the recorded counts are what will show whether 2,000 is right.

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

**2. PLAN.** Before planning, read the experience library's `INDEX.md` beside this file; open only the entries whose cue matches this task, cite each line you use in the plan, and treat it as a hypothesis to re-check against the files, not as a fact (see STUDY YOUR OWN WORK, step 12). Research the best current approach, then write the plan where the profile says. It records: baseline identity, the problem, acceptance criteria, non-goals, the code you actually read, the search and nearest match for every new name, affected components, proposed behaviour, the test strategy and its red command, external-contract evidence, the applicable gates, and how you will deliver and recover. Every claim about current state cites a file, a command result or a source. No detailed spec for a one-line fix.

Name the temporary resources the task will create, how their ownership and safe removal will be checked, and where the final implementation report and retained evidence will live.

**CHECK THE DESIGN WHERE IT CHANGES.** For software changes, including configuration and scripts, answer these questions in the existing plan, including the short `dsf` plan. Keep the answers brief and in proportion to the change. Cite the affected paths and the intended checks. For a question that does not apply, give the reason.

- Where does outside data enter, and where is it checked? Can the existing data types prevent an invalid state?
- Can the changed business logic be checked apart from storage, network calls and other side effects, with a small local change?
- What happens if the operation runs twice, is retried, or stops halfway through? Where repeat safety is needed, how is it proved?
- Do concurrent actors need the same mutable state? Keep independent state separate; where sharing is needed, name its ownership and how updates stay safe.

Use the answers to improve the planned change within its scope. Clear existing code can stay. These questions do not require a rewrite or new infrastructure; step 6 still decides scope.

**3. LOOK UP WHAT YOU ARE ABOUT TO ENCODE.** Before writing any external claim into code, a test, a plan, a review or a commit message, look it up: an external service's contract, a third-party API you depend on, any tool behaviour not settled by its help output or a run. "I already know this" is never an exemption. Rank sources by what each establishes.

A run establishes what THIS BUILD does. Run anything executable in the tree; record version, environment, command, result. It outranks documentation and every reviewer about the machine you are on, never about a remote service. For a pinned dependency, read the locked source your build compiles.

A specification establishes what is GUARANTEED. Where the two disagree, the run wins on behaviour, the specification on guarantees, and code depending on the difference stays INFERRED.

Documentation tooling DISCOVERS; it does not CONFIRM. Use it freely and early, for any language, to find what exists, what a thing is called, the shape of an API, the idiom. A claim resting only on it is INFERRED even when you asked for a version, because such tooling does not reliably scope its answer to the version you named. To reach VERIFIED, confirm the one fact you are encoding against a version-exact source.

If a lookup misses the exact thing, record NOT INDEXED and go upstream: a wrong answer with a citation is worse than an honest INFERRED. Mark every VERIFIED claim with source, version or date, and passage. Where documentation specifies no wording, ordering or guarantee, that silence IS the finding. Re-run this whenever later work introduces a new external claim.

**USE THE LATEST VERSION OF EVERYTHING. Owner decision, 2026-10-17, verbatim:** *"always use the latest versions if anything - programming languages, tools, libraries, frameworks, APIs, check which version of tge latest and how to use it in context7 or Internet before add to a project"*. The rule applies whenever a slice adds, upgrades or pins a programming language, a toolchain, a tool, a library, a framework, a container base image or an external API version. It does not move a pin the slice does not touch, and it covers what the slice names, not the whole dependency graph. **Take the newest stable release.** That is the highest tagged release that is not a pre-release, in any major version, as published on the day you look it up. Do not stay on an older LTS line when a newer stable release exists. A release that comes out after the lookup does not reopen the slice. An API without tags uses the newest version the vendor documents that day. A module with no tagged release at all uses the newest commit on its default branch, and the plan says so. **Look it up before you add it**: which version is the newest, and how that version is used, run and configured. Use the documentation tooling `TOOLING.md` lists to discover it, then confirm against a version-exact source (the official release page, the registry or module proxy, the vendor's changelog), exactly as this step says. The plan records the version, the source and the date. **The project declares the exact version.** Never a floating tag such as `latest`, and never an open range. **Only two things allow an older version.** First, a run shows a real defect in the newest. Then take the newest release without that defect. Second, the newest needs a newer language line or a new major API. That move is its own version slice, and it comes first. Until it lands, take the newest release that works on the current line. Write the version slice to the queue or the backlog with its trigger, and tell the owner. In both cases the plan names the newest, the one chosen, and the evidence. **Slices:** a new dependency comes in the same slice as the code that uses it. Moving an existing dependency to a new version is its own slice, never mixed with a behaviour change. Step 10's pin still decides which version the gates run on. This rule decides what the project declares. **Not covered:** AI model choice and reviewer effort. Step 4 and the machine's model and reviewer policies decide those. Do not pin a model where those policies say not to. An explicit owner decision that pins a version wins until the owner changes it. Record where he made it.

**4. REVIEW THE PLAN.** Freeze the artifact and record its identity. THE FREEZE BINDS YOU: check it yourself before launching, then hold every finding, yours and theirs, until the round closes. Give each reviewer the hash it should see and ask it to report a mismatch.

Use independent reviewers, ONE PER MODEL FAMILY: a second from a family already represented is one opinion counted twice. The profile names which families are PRIMARY and which SUBSTITUTE for a missing one, and how many legs a round runs; a substitute is used only to replace an absent primary, never to add an opinion beyond the number of primaries the profile calls for. Use the newest model each offers, and where the tool has a reasoning-effort setting, at an effort you have decided and written down; resolve both at run time rather than pinning a name, then confirm from the tool's own output which model answered, and at which effort where it reports one. Give each full context, full access and your specific questions. NEVER narrow what a reviewer can see, even if a reviewer suggests it. Confirm each has what you think, with a control question only the project's rules can answer. They are not equally equipped, so record the asymmetry. Assume none is read-only until tested. Ask for the most native, minimal solution that fully does the job, and for a deep review of what you missed. Launch them against the same frozen brief before saving any output; within a round no reviewer sees another's.

DONE when each raw output is saved verbatim to its own file, headed with revision, date, baseline, each reviewer's model and verdict, and any degraded reviewer. A reviewer counts only if it exited cleanly, returned findings or an explicit no-findings verdict, and named the revision it reviewed; an exit code alone does not establish that. If one fails, restart it; if it fails again, try another interface in the same family, then the substitute the profile names. IF IT STILL WILL NOT RUN, TELL ME AT ONCE - naming the leg, its family and the reason - AND CONTINUE THE ROUND WITH THE LEGS THAT REMAIN. A leg that cannot run is a RECORDED DEGRADATION, not a BLOCKED step: it does not stop the slice, and it is never silent. Every artifact carrying that round's verdict states how many legs ran, which were missing, and why - a round run short is never described as a full one. THE FLOOR IS ONE: a round with no leg at all cannot happen and is a stop. A one-leg round states that it was one, and whether that leg SHARES A FAMILY WITH THE AGENT THAT WROTE THE CHANGE - which is the weakest review this flow can produce, because none of the comparison this step is built on happens at all. A LEG RECORDED UNAVAILABLE IS RE-PROBED AT THE START OF EVERY NEW SLICE, before the round is planned: availability is a STATE, not a verdict, and a leg written off from an error string stays written off long after it recovered. Probe on a free surface first - a catalogue or login call. Where no free surface can establish the seat, a MINIMAL probe that spends the least the tool allows is permitted; a review is never a probe. Two different things count as alive and the record names which: the interface is REACHABLE, and the family can RETURN A VALID REVIEW. Where a free probe establishes only the first, record the second as unknown rather than as alive. Record what the probe returned, not what the last failure said. An automatic or on-edit reviewer never substitutes for one: judge its findings, never count it, and a tool scoped to part of the tree says nothing about what it cannot see.

Reviewers are deliberately NOT in conversation. Convergence is agreement, not correctness, and a finding with one author is not weaker for being alone. When two contradict each other on a fact, ask the code: run the command, read the line, write down what it says.

**DO MORE IN EACH ROUND. Owner decision, 2026-10-12.** Aim for about **30% more active work per round** than a single-pass review, not more seats or more rounds. Before the freeze, make a short risk map of the affected paths and claims. For code, include the changed branches, boundary values, alternate valid inputs, constructor/codec paths, and which tests or wrong-code checks cover them; for plans and documents, include the decisions and evidence most likely to be wrong. Check the map yourself and close obvious gaps before launching. Give it to every reviewer as a guide, with the full artifact and full access unchanged. Ask each leg for its normal whole-artifact review **and a second adversarial pass** on the map: try to break the most important unproved claims, run a concrete counterexample where practical, and report all distinct findings and any areas it could not check. Do not stop the review at its first finding, count time as proof, set a finding quota, or turn the map into a limit on what a leg may inspect. Record the added pass in the brief and verdict. The freeze and separate plan and test-plan reviews still apply unless the selected mode says otherwise. The five-round cap and convergence rule apply only in full flow; `dmf` and `dsf` have the two-round rules below.

**5. SYNTHESISE.** Take the strongest argument, not the majority, and verify contested claims yourself. DONE when a register records every finding as ACCEPT, REJECT or DEFER with evidence. A REJECT needs a citation, command or source, and so does an ACCEPT that changes the design. Never require unanimity. A DEFER does not survive the slice: close it with evidence or write it to the backlog with its trigger. Mark a finding `ESCAPED from <round>` when its cause was already in an artifact an earlier round reviewed, or `ESCAPED from delivery` when it was found after delivery. Disagreements evidence cannot settle are MINE: if a dispute turns on a preference between two designs that both satisfy the constraints, stop and put both to me.

RE-REVIEW — full flow only; use the mode rules below for `dmf` and `dsf`. A materially changed artifact is a new revision and goes back through review, including changes made because of a review. Scope it to the delta and its blast radius, same reviewers - meaning the seats the profile calls for, re-probed, not merely the subset that happened to run last time. Fix the cap on rounds before starting, the same for every artifact type: **five, unless I say otherwise.** Fewer needs my agreement and a reason recorded, because a cap is a budget for finding defects and I would rather spend it than ship past it. THE CAP ENDS THE ROUNDS; IT NEVER CONVERTS AN UNREVIEWED FIX INTO A REVIEWED ONE. If the cap falls due with a correction no reviewer has seen, the slice stops and comes to me with that correction named. If findings keep coming past the cap, stop and tell me: that is a signal about the artifact.

**PRODUCT CONVERGENCE ENDS THE ROUNDS — full flow only. Owner decision, 2026-09-20.** Count findings in the **TRACKED CHANGE SET** only. **Two consecutive rounds with zero findings there and the slice SHIPS**, even if reviewers are still finding things in your process artifacts.

Findings in gitignored process artifacts - checkers, freeze scripts, launchers, briefs, plans, gate records - are REAL, and you fix them. **They go to the backlog with a trigger. They never restart the cap, and they are never a reason to open another round.** Nobody ships them.

**This does NOT narrow what a reviewer can see, and it must never be used to.** Legs keep full access to everything, including your tooling, and they SHOULD read it: measured on one slice, three of the most valuable findings of the whole review came from legs reading exactly those files - a fabricated search recorded as evidence, a gate record describing a different revision than the one frozen, and a proof that passed a false document. What changes is only which findings restart the budget.

**THE MEASUREMENT THAT PRODUCED THIS RULE, so it can be checked rather than believed.** One slice, five rounds: the tracked change set went 98 -> 136 -> 150 -> 163 -> 164 insertions, so the last round moved ONE line of product, while the proof was rewritten seven times and one check inside it five times, each version defeated by a reviewer. All legs had said "ship the documents" two rounds earlier. **The findings had stopped landing in the product and started landing in the proof**, which `REVIEWING.md` already names as a signal about the artifact rather than about reviewer quality - this rule is what acts on that signal.

**The failure mode this prevents is LOOPING, not stopping,** and it is self-feeding: on that slice almost every finding in rounds 2 to 4 was in a correction the agent had just made. A higher cap buys more rounds of the same. If findings keep coming in the PRODUCT past the cap, that is the different signal the paragraph below is about, and it still stops.

**6. NO OVERENGINEERING**, from you or a reviewer. Solve exactly the task that exists. Write good extensions to the backlog with their trigger, or to the handoff if there is none. If measurement shows the change is not worth making at all, that is a stop, not your decision.

**RELEASE CANDIDATE FIRST. Owner decision, 2026-10-20, verbatim:** *"for the first developing process we accept only changes which make our app/service closer to the first release candidat which can be run, work and execute it`s main functions. All another changes we add to the future tasks which will permorm after a service/app will be run and work. You can order these tasks from the most important (security, stability, safety) to less important but we will execute them after we will have a working app"*.

**Until a project building an app or service RUNS and does its main functions, build only what brings it closer to that.** Ask of every change, yours or a reviewer's: **does the product need this to run and do its job?** If no, it is a backlog entry, not work - a correct, well-argued, measured change that does not move the product toward running is filed, not built, and that is the failure this rule was written for. **If I asked for it, do not file it yourself: name it and put it to me.** Order the backlog security, stability and safety first, and work it once the service runs.

**It governs SCOPE, never QUALITY.** It removes no step, no gate, no test and no review round from the work you do build, and "closer to running" never excuses skipping one. It ends when the service runs and does its main job.

**Reuse before you build, and ask before you widen.** Before writing anything new, inspect what already
exists here - commands, scripts, APIs, configuration - because the search rule below asks whether a NAME is
taken, not whether the CAPABILITY is already present. **Prefer a small script or an explicit operator step to
new infrastructure** when it meets the agreed need. **A missing capability is not authorization to build it:**
say what is missing and ask. **The approval list:** when a change would touch **another product, authentication, permissions, a database, a dependency or a public API** and that was not part of the task, stop and get my approval - step
9's in-scope plan amendment under the selected mode is yours to do alone, and these are not.

**AGENTS DECIDE AND CONTINUE. Owner correction, 2026-10-27, verbatim:** *"this rule: Owner approval before adding a required  check. broke our main goal - developing nonstop, flow shouldnt stop in the middle of develooing, meximum decisions should be made by agents automatically, based on our flow rules"*.

Within already authorized work, make routine engineering decisions yourself using this flow, the project's rules and evidence. Choose a supported option, record why, and continue in the same turn. This includes local design, implementation, test strategy and project-check choices within the approved scope. Follow the normal plan-amendment, test, review and delivery rules. Ask only when the applicable rules actually require new owner input, and honor authorization already given. Do not add approval steps for routine choices. An optional tool suggestion alone is not a blocker.

Every NEW name - symbol, field, file, table, dependency, package - is a claim that nothing here already carries this. Record the exact search you ran and the nearest thing it found, in the plan, where the reviewers see it before the code exists. Untidy is not unfit; incorrect is.

**7. TEST PLAN: its own document, its own review stage**, permanently separate from the plan. A design review asks whether the change is right; a test review asks whether the proof would catch it being wrong. Merging them lets whoever decided the first answer the second.

**8. TESTS FIRST, WITH THE RED RECORDED.** Write the tests and run them. DONE when you have the exact command, exit code, verbatim failing output, and one line saying why the failure is the missing behaviour and not a compile error or a bad fixture. A test that passes before the implementation exists is not a test of this change: find out why first. Anything touching timing, concurrency or shared state runs under the toolchain's race or hazard detector, repeated enough to trust; if there is none, say so and name what you ran instead. Never weaken, skip or delete a test to get green.

**9. IMPLEMENT** the minimum reviewed design. If it needs an unplanned file, symbol, dependency, config field or behaviour: stop, amend the plan and test strategy, redo the affected lookups, and follow the selected mode's re-review or amendment rules - except where step 6's approval list reserves it for me, which you cannot settle alone. DONE when the change matches the recorded scope, or every deviation has a disposition. Then make one pass whose only goal is finding code this slice added that should be deleted, inlined or replaced with reuse. Reviewers are the last to notice absence.

**10. GATES BEFORE EYES.** Run every category the project HAS: format; the full test suite; the concurrency detector; type and static analysis; the linter; dependency vulnerability and provenance; dead code; and a production build of EVERY CONFIGURATION THAT SHIPS. Each gets its OWN state; never bundle them into one result that can be neither honestly PASS nor honestly NOT TRIGGERED. Pin the toolchain to the version the project declares: a result from a newer one is not evidence about a project targeting an older one. Where a category has no runnable command, that absence is itself a finding: record the ad-hoc command and its output, and never report a category as covered by a target that does not exist. DONE when commands, versions, exit codes and output are recorded. "It passed for me" is not a result.

**OPTIONAL COMPLEXITY AND DUPLICATION TRIALS.** Reuse the project's existing checks first. `TOOLING.md` describes an optional trial on one project, with measured findings and resource use. You may choose a trial or adopt an evidence-backed project check within already authorized work, under step 6 and the normal test, review and delivery rules. Record the reason, evidence, command, scope and success criterion in the project profile. No separate owner approval is needed for this routine decision. Until adopted, a trial is advisory: its absence is not BLOCKED, and its results replace none of the required gates or reviews. There is no shared numeric threshold.

**A REPORT OF SUCCESS IS NOT EVIDENCE OF SUCCESS. RE-READ THE ARTIFACT.** Your own script saying it applied a fix, your own generator printing a gate record, your own harness reporting a pass - none of those is the thing itself. **Measured FIVE times in one slice:** a `printf` placeholder sat where an exit code should have been; a patch script wrote the file before two later edits ran and printed both as applied; a falsification test reported the attack still passing because the patcher had a missing argument and had patched nothing; another patcher wrote literal newlines and left the checker unparseable; and a gate record was generated before the change was staged, so it described the previous revision. Every one was caught the same way - by running the thing and reading the file - and not one was caught by the message the tool printed.

This applies to DOCUMENTS too: before an artifact reaches a reviewer, resolve every file and line citation and fail on a blank line or missing file, resolve every named symbol and path, and never assert a count beside one that can be computed.

**MUTATION CHECKS: SCOPED BETWEEN ROUNDS, FULL BEFORE DELIVERY.** Where a slice has a mutation check (wrong versions of the code that the tests must fail), it is evidence about the tests, and it is expensive. The first run of a set is full. Between review rounds and after a fix, rerun at least the mutants whose edit touches a file changed since the last full run, whose killing test is in such a file, or that were not killed in the last run. Add one new mutant for each new or changed condition in production code; each new test row must kill at least one mutant. "Changed" means the diff between the tree of the last full run and the current tree, so a rebase counts. Run the full set on the final change set before step 12. Every gate record says whether its mutation run was scoped or full, and names the revision or snapshot identity of the tree the last full run tested; if that tree cannot be named, the next run is full. A mutant that does not apply or does not build is neither a kill nor a survivor: it is a defect in the check, and it is fixed before the run counts. A hang, or a crash that names no failing test, counts as a kill only when it happens again on a second run and the same command, with the same time limit, passes without the mutant; otherwise it too is a defect in the check. A mutant removed from the set is recorded with its reason. The other gates of step 10 are never scoped.

**11. REVIEW THE CHANGE**, same rules as step 4. Freeze the complete change set INCLUDING FILES NOT YET TRACKED and review against exactly that. Ask for unnecessary code and overloaded implementation. Look up any reviewer claim about an external contract, exactly like your own. Fix what is genuinely wrong and follow the selected mode's review budget: full-flow re-review and cap, or the two-round `dmf` / `dsf` rules below. A fix that never went back through review is unreviewed. Then run all the tests. If you cannot finish a test, that is BLOCKED: write the message for whoever picks it up and stop. It is not permission to commit or deploy.

**12. DELIVER, THEN PROVE IT.** Commit and push through a merge or pull request: focused commits on a branch, onto the integration branch, never pushed to it directly. Verify the tree contains only this slice and that every new file was in the review scope. A disabled or absent pipeline is not a green pipeline: the step-10 record is then the only evidence, so put commands, versions and exit codes in the request itself and never call it CI-green.

Then deploy and prove it works outside the test suite. Confirm first that what is running is what you think is running. Name which exit condition applies: a behaviour change is exercised on the environment against the behaviour you changed, with the evidence pasted; where the only real proof is an action with an external side effect, perform that action for real; a build or packaging change runs the new command in every configuration that ships; a user interface is exercised through the browser-driving tooling the profile names, front end and back end both; a docs-only change records "docs only, no runtime surface", which is the exit condition, not a skip. Define the rollback first and check it is SYMMETRIC. If verification fails, roll back or fix forward before the next slice, and a fix-forward re-enters at step 9. Without deployment authority, finish as READY_FOR_DEPLOYMENT with exact deploy, smoke-test and rollback instructions, and stop.

**Update the documentation this change makes stale, in the same slice.** A document that still describes
behaviour the change removed is a defect the change created, and leaving it is how the next agent is misled.

**FINAL IMPLEMENTATION REPORT AND CLEANUP. Owner instruction, 2026-10-24.** Apply this at each completed slice and again when the whole task is finished, in full flow, `dmf` and `dsf`. Passing tests alone is not completion: first satisfy the required gates, reviews, delivery and verification above. At a blocked or READY_FOR_DEPLOYMENT stop, update the same working-plan report with the real state, kept resources, the next responsible actor/action and the condition for cleanup. Keep the material still needed to finish or investigate the work. The resuming agent updates that report and revisits cleanup when the missing proof succeeds. For cancelled or abandoned work, record that outcome and use the same retention and safe-cleanup rules without claiming successful delivery.

**Use `dsf` for the final report and cleanup phase, including after a task that used `dmf` or full flow.** Reuse the existing task plan and evidence. When this phase changes no tracked content, do not start a new slice, MR or cycle of project checks or reviews solely for completion facts and verified cleanup. Any tracked edit is outside this completion phase and follows the flow, review and delivery rules for that edit. The main task must still pass its own required tests, reviews, delivery and verification. All evidence-retention and safe-cleanup rules below still apply. This includes report readback, ownership/current-use checks and post-cleanup verification.

**Update the implementation plan with the final implementation report.** Define its durable retained working-plan/report path before review; use persistent project storage, not a temporary directory. Keep it available to the intended follow-up agents. Draft known implementation facts in the plan before final review; append observed delivery, verification and cleanup facts afterward as a dated revision. If the frozen plan is tracked, include those known facts and a stable pointer to the retained working copy outside the tracked tree before the final review freeze, and finalize the report there. The pointer and handoff give the access or restore steps needed by future agents. Any later tracked edit still follows the existing review/delivery rules; do not create a new implementation slice solely to record observed completion facts in the retained working copy. Keep the exact reviewed/frozen plan bytes and their recorded identity before updating the working plan; do not rewrite the original intent to make it fit the result. Keep earlier report revisions in retained evidence when later work changes the result. At whole-task completion use the task plan, or, if there is none, the final slice's retained working plan with a consolidated outcome and an index of all slice reports. The report must give a future agent enough context to correct or extend the task without its old conversation or disposable working folders. Scale detail to the actual change; for a category that does not apply, say none or NOT TRIGGERED and why. Include:

- the original goal, scope and acceptance criteria; what was actually delivered and how its behavior differs from the baseline;
- the baseline, final source and delivered revision identities, commits and merge/pull-request links, and the exact files, modules, interfaces, configuration and data changes involved;
- the final design and how the parts work together; the important decisions, reasons, alternatives rejected, and deviations from the reviewed plan, with their evidence;
- the exact check commands, tool/dependency versions and relevant environment, exit codes, results and retained evidence paths; distinguish local checks from CI, and record failed-baseline, NOT TRIGGERED or unavailable checks honestly;
- the full review-output and finding-register paths, and any fixes marked "fixed after the second review, not re-reviewed";
- the actual deployment state and verified environment/revision; the commands and paths needed to reproduce, run, validate, recover and roll back the result, including required inputs and configuration names but no credential values;
- known limits, remaining risks, deferred work and its trigger, the next concrete entry point for a follow-up, and where its necessary source, decisions and full evidence can be found;
- the cleanup outcome: exact resource paths or IDs, cleanup commands and results, measured space recovered where available, and anything kept or deferred with its reason and the condition for revisiting it.

Use concrete references and facts, not a claim that everything passed. Read back the saved report and check its references against the final work. The handoff names this report path; a short handoff must not replace the report.

**Remove the task's temporary objects after preserving the return-to-task context.** First save and verify the report, the required original/frozen inputs, full review outputs, validation evidence and deployment/rollback records in the project's retained-evidence location. When a compact archive replaces disposable working copies, retain the full required bytes, record its path, checksum and restore command, and verify that it can be restored before deleting those copies. A summary or a hash alone does not replace evidence the flow requires.

Then remove every no-longer-needed temporary object created for this task: isolated caches, build/test outputs and binaries, copied review/build trees, temporary files, unpacked downloads/images, and task-only test containers, volumes, networks or other temporary resources. Use exact targets and native scoped cleanup commands where available. Before each removal, verify the object's task ownership and purpose and check for current use by processes, containers, mounts, other agent sessions and remaining slices. An old timestamp, a name containing "cache", or a tool calling an object "unused" is not enough.

Keep the delivered product and its source, uncommitted work, live application/user data, saved sessions, required evidence, and resources needed to run, deploy or roll back. Do not clear a shared/global cache, another task's files or a whole temporary root to satisfy this task's cleanup. If ownership or safety cannot be proved, keep the object and record why. Report removal errors and incomplete cleanup; never mark a failed removal as cleaned. After cleanup, verify the retained report/evidence and delivered result still exist and work, and record the actual cleanup outcome in the report before the handoff.

CLEAR CONTEXT AFTER EACH SLICE. First write a handoff naming the finished slice, the baseline identity, the PATHS of the review outputs, the validation results, the deployment state, EVERY SLICE STILL OUTSTANDING IN ORDER, and the exact next step. The boundary is a pause, not a stop.

**STUDY YOUR OWN WORK. Owner decision, 2026-10-19, verbatim:** *"The best size it`s exactly for that this harness - agents stady and make itself better and improve a behaive - this is that we should implement"*, and on who checks a lesson: *"A main session who run it"*. The method is taken from harness2 (google-research, arXiv 2610.14224): a record per task and a library read before the next one. **No size cap on the always-on instructions**: the owner rejected it in the same decision. `TOKEN-BUDGET.md` is unchanged by this.

- **When.** In the handoff, if the owner corrected the agent, a finding was marked ESCAPED, or the project's `postmortem-fix` skill ran, write one record to `experience/candidates/<slice>.md` in the format at the top of `experience/INDEX.md`. Otherwise the handoff says `NO_ENTRY` and names the three checks that were empty. A missing record is a gap in the handoff, not a BLOCKED step.
- **Evidence.** Each row names its oracle: a command and exit code, a register id, or the owner's words quoted. The author's own prose is never evidence. `confounded` is the default when one slice or several changes stand behind a difference, and `NO_ENTRY` is a normal answer. A lesson whose rows are all `confounded` or `oracle: none` is not accepted.
- **Acceptance.** A candidate is never read as a lesson until it is accepted. The main session that ran the slice accepts or drops it: it re-checks every row against its oracle (re-runs the command, re-reads the register line or the owner's quote) and accepts only a lesson the evidence supports as written. A lesson that IS the owner's own quoted words needs no other support; a lesson the agent drew from his words is re-checked like any other. Accepting means: the next `E-NNNN` id, the file in `entries/`, its INDEX row, and one commit in the instruction repository at the handoff naming the slice. A dropped candidate stays, marked `status: dropped`, so it is not written again as new.
- **Lessons never outrank written rules.** Where a lesson conflicts with this flow, a project instruction file or an owner decision, the written rule holds and the lesson goes to the owner. `removes-or-relaxes-a-check` is `yes` by rule, not by the author's choice, whenever the lesson would skip, shorten or weaken a step, a gate, a review or anything in the never-self-edited list below.
- **From lesson to behaviour.** At step 2 a lesson informs the plan as a hypothesis. A lesson changes the harness (the flow, instruction files, hooks, scripts, skills) only through a later slice that edits one named component, preferring in this order a hook or test, a script, a skill or on-demand file, and always-on prose only if it holds for every task, in one commit that names the lesson. Until the known-defect corpus (`TOKEN-BUDGET.md` §13) has an item to probe it, an always-on prose edit from a lesson is a forward trial and its verdict stays `confounded` until its measure moves. Rollback is reverting that commit and setting the entry `status: retired`.
- **Never self-edited.** The owner's verbatim decisions, the stop list, the reviewer rules and validity gates, BLOCKED, the dsf trigger list, the auto-decide exclusions, Tier-1 gates, hooks and killswitches, and this paragraph. An agent may only propose a change to them. Auto-decide never adopts a harness change. A lesson marked `removes-or-relaxes-a-check: yes` goes to the owner.
- **Curation, never a cap.** Two entries with the same cue are merged by the review that sees them. A lesson that `hurt` is retired and stays visible. A superseded verdict leaves the always-on file and git keeps it; the measurements behind it may stay, marked SUPERSEDED, or move to an on-demand file. The owner's own text leaves only with his yes.

**FINISHING A SLICE IS NOT A REASON TO STOP. Owner instruction, 2026-09-20.** A merged MR, a green gate record, a closed review round, a written handoff and a cleared context are all the MIDDLE of the work. When a slice ends and nothing is blocked, the next action is to START THE NEXT SLICE IN THE SAME TURN - look it up, do not decide it: the profile names where the queue lives, and its top entry carries the literal command. Report what landed and take that next step in one message. **A message that ends with a finished slice and no tool call has stopped, and stopping there is the defect this paragraph exists to prevent.** It has happened repeatedly, and every time it looked like diligence rather than like quitting.

DON'T STOP UNTIL THE IMPLEMENTATION IS FINISHED. **THERE IS EXACTLY ONE REASON TO STOP: A REAL BLOCKER, AND THE LIST IN THIS PARAGRAPH IS THAT LIST.** Nothing outside it is a stop, however natural a pause it feels like. Going back a step to amend and re-review is not stopping. Finishing a slice is not stopping. Neither is a merged MR, a closed review round, a green pipeline, a handoff, a cleared context, or running out of things that felt urgent. A stop is when you need me: a credential only I hold; a decision only I can make, including whether a slice I asked for should not be built; a permission you were denied; a review gate that needs my reply; an escalation asking for my choice, which you forward verbatim; a round with NO reviewer leg left at all - a single missing leg is reported and continued past, never stopped on; the full-flow cap falling due on an unreviewed correction; a required test you cannot finish; no deployment authority; a credential exposed in an artifact; or a disagreement evidence cannot settle. Any step recorded BLOCKED is one of these. Say what is blocked, the last reviewed identity, and the exact action you need from me.

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

**FLOW SELECTION — `dmf` IS THE DEFAULT. Owner instruction, 2026-10-28, verbatim:** *"ok, we need one more regime - "do medium flow" it`s between full and dsf flow, like full but only with two reviewes on each stage (plan, tests, changes) and make this flow default"*.

Choose the mode once at the start of each new slice and record it and its trigger in the plan and MR:

1. A mode explicitly requested by the owner for the current task wins: `dmf` / "do medium flow", `dsf` / "do the simpler flow", or "full flow". This includes an explicit choice for a prose-only task. A specific owner-approved project regime or owner-ordered queued mode applies when the current task does not override it. Keep that project regime's own recorded stage artifacts and cap behavior within its authorized scope; do not silently rename it `dmf`. A project or queue regime alone does not override automatic prose-only `dsf` unless the owner expressly included prose or selected a mode for the current task.
2. Otherwise keep the existing `dsf` cases: prose-only work, and the agent's permitted choice for simple work below. Step 12's report and cleanup phase always uses `dsf` without changing the main task's mode.
3. All other work uses **`dmf`**, including big tasks, shipping code, tests, configuration and work that is not eligible for an agent-selected `dsf`. Choose the full flow only when the owner requests it; size alone does not select it.

This replaces the older automatic full-flow fallbacks in the `dsf` history below. An agent-written queue label from a standing binary `dsf`/full classification of "full flow" that only classified an item as not eligible for `dsf` now means the default `dmf` for a new slice. Generic "use full flow" boilerplate and earlier general preferences for full rather than `dsf` do not override this newer `dmf` default. They are not a specific owner exception. Keep full flow when the owner specifically chose its review regime, rather than that old automatic classification. A slice already running when this instruction takes effect keeps its recorded mode unless the owner directs a change, including that mode's eligibility and escalation checks. Recheck automatic `dsf` eligibility whenever the work changes, including in an already-running slice; use the software-scope transition below if prose gains executable work. Retain completed review evidence and record any mode change, never rewrite its history. These are flow choices, not new scope or deployment permissions. For a project conflict not settled by an owner decision, use this file's opening precedence rule: project commands/paths win, while a removed required step is a stop.

**`dmf` — DO MEDIUM FLOW.** Keep all twelve full-flow steps, including the full implementation plan, its review, a separate test-plan document and its review, tests first with the red recorded, implementation, all applicable gates, final change review, delivery proof, report and safe cleanup. A surface that does not exist is still NOT TRIGGERED with evidence.

**Exactly TWO rounds at each review stage, independently:**

| stage | artifact | rounds |
|---|---|---|
| plan, steps 4–5 | implementation plan | 2 |
| tests, step 7 | separate test plan | 2 |
| changes, step 11 | complete final change set | 2 |

All three stages are required in `dmf`, including an explicitly selected `dmf` on prose: its separate test plan describes the applicable document checks and records absent runtime tests as NOT TRIGGERED. A round means the normal independent reviewer legs in step 4 and the machine profile, not one reviewer. Reviewer families, quota fallbacks, probes, full access, freeze identities, validity checks, findings registers, degraded-round reporting and the zero-leg stop all stay. Two rounds happen even when round 1 is clean. Freeze each round; resolve round 1's findings, then give round 2 the corrected artifact, delta, blast radius and one-line disposition ledger. When round 1 changed nothing, round 2 is a fresh whole-artifact review with the first round's ledger; an empty delta is not an empty review. Each stage asks its own question: is the plan right, would the test plan catch it being wrong, and are the final change and its proof right?

**The two-round budget replaces full-flow re-review and convergence, not the evidence or fixes.** No third round at a stage, no two-clean-round requirement and no five-round cap in `dmf`. Resolve every finding under step 5. Corrections after round 2 are recorded in the plan, relevant register and MR as "fixed after the second review, not re-reviewed", with the stage, changed paths and checks. Finish the checks required at that stage before advancing; later stages keep their own test and gate order. The budget ending with such a correction is not itself a stop or a request for approval. Real BLOCKED conditions and owner-only scope decisions remain stops.

For an in-scope change under step 9, amend the implementation plan and test strategy, redo affected lookups, and use any remaining rounds of the affected stage. If its two rounds have already run, disclose the later delta as unreviewed at that stage and include it in every remaining applicable stage's context. Final change reviewers read the current plan, test plan and complete change set, including these deltas. Never reset a stage's spent budget, open a third round, or split the same scope solely to buy more reviews. Tests still go red before implementation, including a correction after round 2; a real new scope follows the existing slice and approval rules.

**Full flow remains available.** When selected, use all twelve steps and the existing RE-REVIEW, five-round cap, cap escalation and PRODUCT CONVERGENCE rules unchanged. `dmf` changes only the review budget and how its later corrections are recorded; `dsf` additionally drops the plan and separate test-plan reviews as described below.

**`dsf` — DO THE SIMPLER FLOW. Owner instruction, 2026-09-23, verbatim:** *"Can we add an alias in our
main developing flow - dsf - do the simpler flow - it`s mean that if I write it in task flow should be
simpler - only one final review and only final tests"*. **Corrected by the owner on 2026-09-24, verbatim:**
*"Can you correct dsf flow - tests before code should be stay but review should be only one in final;"*. So
tests still come FIRST, with the red recorded. What `dsf` shrinks is the reviews - to one, at the end - and the
plan and the test plan, which become one short plan.

**When it is on.** Apply FLOW SELECTION above first. Step 12's final report and cleanup phase always uses `dsf`, even after a `dmf` or full-flow task (owner instruction, 2026-10-24); the main task keeps its own flow. When I write `dsf` in a task. When a project's queue or backlog marks an item for "a
simpler flow" on my order. **And ALWAYS for a docs-only change.** Owner, 2026-09-23, verbatim: *"can you
add that for documentations, instructions we always should use dsf"*. A change is docs-only when it changes
only prose: documentation, READMEs, instruction and rule files, plans, registers, queues, and comments. It is
NOT docs-only if it changes code, tests, configuration (permission settings, CI and build files included),
or an example that a test or an operator runs as it is, such as a config block or a command. If a docs-only
slice turns out to need such a change, record the prose slice's real state and continue the executable work in a separate software slice, within the same authorized task. Select its mode under FLOW SELECTION (`dmf` by default); finish its plan and test-plan reviews and red test before implementation, then its change reviews. Preserve the prose reviews as history; they do not count against the new software slice's review stages. This is a new executable scope, not permission to reset reviews for an unchanged scope. Existing step 6 approval boundaries still apply. An explicit owner-selected `dsf` for executable work remains valid. **You may also choose it yourself for simple work.** Owner decision, 2026-10-20, verbatim: *"Use full flow
for a big tasks and slices, for a simple work with a few commands or documentation creation use dsf"*, and
when asked whether to reverse the earlier rule that you never choose it: *"a. Yes, let`s you choose"*.
The 2026-10-28 default above supersedes only this older decision's automatic choice of full flow; its limits on agent-selected `dsf` remain. **Simple means a few commands.** It is NOT simple, and `dmf` applies unless the owner selected another mode, if the change touches code that
ships, a test, configuration, a process or launcher script, anything on step 6's approval list, or anything
**outward-facing or hard to reverse** - the same class the auto-decide exclusions name. When in doubt it is
not simple. Nothing else turns `dsf` on. Record which of these turned it on, in the plan and in the
MR. For step 12's completion phase with no tracked content changes, record the trigger in the existing task report instead of a new MR.

**What `dsf` drops - and nothing else:**

- the plan review rounds (steps 4-5 for the plan). Write a short plan instead (step 2): the problem, the
  change, the files, step 2's design answers for software changes, step 6's search and nearest match
  for every new name, the experience lines used (step 2),
  the test strategy with its red command, the task's temporary resources and safe-removal checks, and the
  retained working-plan/report and evidence paths. The final review reads it;
- the separate test plan and its review stage (step 7);
- every review before the final TWO, and every review after them: the RE-REVIEW rule, its cap, the two clean
  rounds of PRODUCT CONVERGENCE, and step 9's "re-review" of an unplanned change (add it to the short plan
  instead). So a fix made after the SECOND review round is not the full-flow stop for an unreviewed correction at the cap;

- a project's own rule that requires one of these steps, such as a separate test-plan review.

**What `dsf` keeps: everything else, unchanged.** In particular:

- **tests first, with the red recorded: step 8, in full and unchanged.** That holds for every piece of code,
  including a fix made after the review and an unplanned change: its failing test comes first. For a docs-only
  change there is no code, so step 8 is recorded as NOT TRIGGERED, not as "dsf: not run";
- **the final tests:** every gate the project has (step 10), on the final change set. Run them before the
  review, and again after any fix;
- **TWO final review rounds** (step 11) on the final change set, frozen, with the reviewer legs step 4
  calls for. **Owner decision, 2026-10-23, verbatim:** *"Let`s correct dsf regime in our main flow for 2
  review rounds instead of one"*. It replaces the single round `dsf` carried until that date.

  Ask each round both questions: is the change right, and would its tests catch it being wrong? Every
  finding still gets ACCEPT, REJECT or DEFER with evidence, as step 5 says. Fix what is really wrong.

  **The second round is what the first one cannot be: a review of the FIXES.** Round 1's corrections go
  into the change set and round 2 reviews them like any other code. That closes the gap a single round
  leaves, where every fix ships unread. **Round 2 is frozen on the corrected change set**, and it is a
  delta round: give it the delta, its blast radius, and a one-line disposition ledger of round 1. If round 1
  changed nothing, use a fresh whole-artifact review with that ledger instead of an empty delta review.

  **Only round 2's own fixes are unreviewed**, and the MR lists each one as "fixed after the second
  review, not re-reviewed", together with any file such a fix adds. **Two clean rounds are not required**
  - that is PRODUCT CONVERGENCE, which `dsf` still drops. Two rounds happen, then the slice delivers;

- delivery (step 12) and its proof.

**`dsf` is less process, not less honesty.** A dropped step is recorded as "dsf: not run", never as PASS.
