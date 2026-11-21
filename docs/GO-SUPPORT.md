# Go 1.27+ support

Read this guide for Go planning, setup, development or review. Choose project
gates during normal Delivery Flow planning. The optional setup in this guide
requires the project-only answer from [Optional tools](OPTIONAL-TOOLS.md).
Use the ordinary profile and its current authority, readiness and rollback rules.

## Discover the project

Before optional consent, read local project metadata. Find project-owned Go
sources and `go.mod`, any `go.work`, CI pins and existing instructions, gates and
client entries. Skip `vendor` and `testdata` when looking for owner modules by
default. Record the actual module boundaries and note an outer workspace or
conflicting CI pin. Keep existing requirements. Defer optional Go commands and
unchosen server checks during this passive inspection.

With a covering project yes, assess each owner module's `go` directive. Modules
below Go 1.27 use the ordinary flow and stay outside this enhancement until
an authorized upgrade. Assess mixed workspaces by module. Older transitive
dependencies do not make a supported owner module ineligible. [Go toolchains](https://go.dev/doc/toolchain)
distinguishes the `go` minimum from the `toolchain` preference.

Check the actual compiler and workspace from the intended module or workspace
directory, after optional setup consent or as part of authorized Go work.

```sh
go version
go env GOVERSION GOTOOLCHAIN GOMOD GOWORK
```

With `GOTOOLCHAIN=auto`, Go may select or download a toolchain, including when
gopls starts Go commands. Check the permitted download effects before running
these probes. Keep existing pins. When an approved new project needs a
toolchain, resolve the newest stable release from the [Go release history](https://go.dev/doc/devel/release)
unless the operator has pinned a supported version. Inspect `go mod init` output
during authorized module creation. Set directives only as needed for the
approved target. This example deliberately sets a 1.27.0 language minimum and
prefers the stable compiler verified on 2026-11-20.

```go
module example.com/myservice

go 1.27.0
toolchain go1.27.4
```

For an empty workspace, scoped guidance and declarations can be prepared after
yes. Record the semantic check as `PENDING_WORKSPACE`. Create a Go module only
as part of authorized application work.

## Choose and verify the binary

Configure the clients used on the project. Reuse a compatible, authorized gopls
and healthy existing integration. Record their effective path, version and
scope. If a new binary is needed, find the newest stable compatible gopls from
the official releases and verify its Go requirement. For example, the
[v0.24.0 release](https://go.dev/gopls/release/v0.24.0) was verified on 2026-11-20.

Before installing, check `GOBIN` or the effective `GOPATH/bin`. Choose a
non-overwriting OS-user tool directory outside the project. Preserve other
clients' binaries and user settings. Keep gopls out of application
dependencies and tool requirements. Use the current user and an exact release
tag. Avoid system installs, persistent `go env -w` or global PATH, `GOFLAGS`,
`GOAMD64` or `GOEXPERIMENT` changes.

Use the selected directory in the install process. This is POSIX shell syntax.

```sh
GOBIN="<selected-absolute-tool-directory>" go install golang.org/x/tools/gopls@v0.24.0
"<selected-absolute-tool-directory>/gopls" version
```

Verify the executable and version from the intended client launch, including
its PATH and working directory. Use a supported project or process environment
where available. If a normal launch finds a different binary, record what it
actually used and explain how to launch with the selected directory on PATH.
For example, a POSIX shell can start Claude with
`PATH="<selected-tool-directory>:$PATH" claude` for that process. Confirm the
equivalent launch in the client's real environment. Only a compatible binary
with real evidence is usable. Reconcile when the choice, client, version or
workspace changes. Reuse current proof and configuration when relevant state
is unchanged.

For every client, defer a setup write that could affect an active slice or
reviewer. Verify the change in the next applicable session. Do not restart,
clear or reload an active worker. When client settings, Go guidance or marked
references are tracked, the changes can reach other users of the repository.
Deliver them through the project's normal flow. Each user keeps control of
their client trust and tool permissions.

## Claude Code terminal

Use Anthropic's official `gopls-lsp` plugin with the existing configured
official marketplace. Delivery Flow is distributed from its public Git
repository and adds no marketplace. If the official source is absent, record
the adapter unavailable and use Go's normal tools. Check the installed
client's help, marketplace listing and effective settings before installation.
The recommendation dialog's install can use user scope. Use the documented
[project-scope command](https://code.claude.com/docs/en/plugins/cli-reference).

```sh
claude plugin install gopls-lsp@claude-plugins-official --scope project
```

Inspect the intended project enablement, shared plugin cache and record writes.
Preserve unrelated JSON and managed restrictions. A needed user-level setting
requires targeted authority. An existing operator-owned integration keeps its
ownership. Record the effective plugin version and source when observed.
Plugin updates outside Delivery Flow can change what a later session loads.

Check native workspace trust and plugin loading. Leave approval and trust to
the operator. Headless behavior alone cannot establish trust. Use supported
`/reload-plugins` only in idle initial setup when it is safe.

Follow the [native diagnostics check](https://code.claude.com/docs/en/plugins/code-intelligence)
in a separate disposable fixture with equivalent project-scoped enablement
and client launch. Verify the intended project's loaded plugin separately.
Observe the actual type diagnostic after a known fixture edit. Restore the
file and confirm the type error is gone. Before removing the fixture, use the
native project-scope uninstall with `--keep-data` for its Flow-owned install
and verify no record still names that fixture. If safe uninstall is unavailable,
retain the fixture and record why. Record client receipt and any model-visible
result separately. Claude cloud does not
start plugin language servers. Verify any approved remote MCP route in its own
environment, including its tool, project and permissions.

## Codex and conditional Claude MCP

In a trusted Codex project, use a targeted TOML-aware update to
`.codex/config.toml`. Re-read current contents before writing and preserve
unrelated keys, comments and operator-owned entries. Keep a conflicting server
until it can be reconciled. Use the [Codex project configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).
Use this project file for setup.

```toml
[mcp_servers.gopls]
command = "gopls"
args = ["mcp"]
```

Specify `cwd` only when the real workspace needs it and the client's
interpretation is verified and portable. Keep machine-only executable paths
out of tracked files. Check project trust and the actual loaded server in the
intended session. An untrusted or pending session may have a declaration while
its client has yet to enable it. Leave approval to the operator and reconcile
loaded state on a later change of trust.

Claude terminal uses LSP by default. Use Claude MCP only on an explicit
operator request, a supported approved remote route, or evidence from the
comparison below that supports adopting it within scope. A supported local
[project MCP configuration](https://code.claude.com/docs/en/mcp) uses stdio.

```sh
claude mcp add --scope project gopls -- gopls mcp
```

Inspect `.mcp.json`, project server approval, effective process CWD and PATH.
Cloud sessions need their own verified route. Keep gopls MCP on stdio for this
setup. Discover the actual experimental server tools from its live catalogue.
Call a read-only semantic operation, such as `go_workspace` when advertised.
Check that it returned meaningful data for the intended module. A registration
or listing does not pass this check. [Official gopls MCP guide](https://go.dev/gopls/features/mcp)

Only where Go MCP is enabled, generate its instructions with the binary the
client uses. Use the project's chosen guide path. Record the exact binary
version and source alongside the output and make it reachable from one
client-specific, on-demand reference.

```sh
gopls mcp -instructions > docs/agents/gopls-mcp-instructions.md
```

Check current enablement before using generated MCP instructions, including
after trust or approval changes. For LSP-only setup this file is unnecessary.
If an authorized gopls update affects an enabled MCP, regenerate it and
re-probe. For LSP only, revalidate native diagnostics where needed.

Record **Operator-enabled**, **configured**, **client-enabled** and **usable**
separately, with scope, dated decision, actual versions, source, commands,
proof, exact owned writes, fallback and missing evidence. Use yes/no/unverified
or `PENDING_WORKSPACE` for usability as applicable. Keep the user's decision
when a tool fails. Required gates have their own evidence and status.

## Project instructions and upgrades

After consent, use one short on-demand project guide such as
`docs/agents/GO.md` if it fits the existing layout. Inspect the actual
`CLAUDE.md`, `AGENTS.md` and shared imports first. Add the smallest marked
reference to the effective load paths and verify each intended client reads it.
When clients share an instruction file, reuse the reference. Preserve the
surrounding content.

```markdown
<!-- delivery-flow:go:start -->
For Go tasks, verify the module's declared Go version and selected toolchain,
then read docs/agents/GO.md. Use available semantic navigation for symbol
questions and official, version-exact sources. Run the project's required Go
checks. In an authorized Go upgrade, review version-sensitive guidance in
the same slice. If Go MCP is enabled in this client, read its versioned
instructions before using it.
<!-- delivery-flow:go:end -->
```

Cover module versions, package boundaries, cancellation and goroutine ownership,
error wrapping with `%w` and `errors.Is`, testing, benchmarks, fuzzing, dependency
and security checks, and the actual project runner. Use
[Go Code Review Comments](https://go.dev/wiki/CodeReviewComments),
[Google's Go Style Guide](https://google.github.io/styleguide/go/), and the
[release notes for the active Go line](https://go.dev/doc/go1.27).
Confirm APIs with local `go doc`, locked sources and exact official references.
Use appropriate literal and semantic searches. Keep one guide with relevant
version references, without importing project-specific third-party rule packs.

When an authorized slice changes a module Go version, toolchain directive,
workspace, build/CI Go pin or applicable Go feature, check affected paths and
versioned sources in that slice. A minor upgrade reviews changes to syntax,
APIs, vet, fix, compiler/runtime and gates. A patch reviews the release changes
and records either the affected guidance or a reason for no change. Inspect
compiler settings in real CI and container builds. Respect the module's
language minimum and `//go:build go1.N` constraints.

## Project gates

Use the project's test, build and CI commands during normal steps 1 and 2.
Record each applicable category and the exact pinned toolchain and runner.
Keep all existing binding gates and their order. Choose and record the gate
strategy for a new Go project within authorized work, without a separate
setup or owner approval step. Optional assistance yes, no and undecided use
the same gates. Optional findings on an existing project stay advisory until
adopted through its flow. Use a supported substitute where the original proof
allows it, or record required missing proof as BLOCKED.

For new Go 1.27+ projects, start with these categories. Run each command in its
valid module or workspace context and verify applicability.

| Category | Example check | Policy |
| --- | --- | --- |
| Build | `go build -mod=readonly ./...` | Required default. |
| Tests | `go test -count=1 -shuffle=on ./...` | Required default. Focused tests are useful during development. |
| Vet | `go vet ./...` | Required default. |
| Format | `gofmt -l` on relevant project files | Required default. Use the project vendor and generated-file policy to select owned files. PASS needs exit 0 and empty output. |
| Race | `go test -race -count=1 ./...` | Required for new Go projects with runnable tests. Use a supported GOOS/GOARCH and cgo runner, or a permitted capable CI runner. If required proof stays unavailable, mark BLOCKED. |
| Module integrity | `go mod tidy -diff` per module | Required default after module creation. A diff can make the command exit nonzero. |
| Static analysis | `go tool staticcheck ./...` | Select an authorized pinned tool where appropriate. Reuse existing lint coverage. |
| Vulnerabilities | `go tool govulncheck ./...` | Select an authorized pinned invocation where appropriate. If required and the scan or DB is unavailable, mark BLOCKED. |
| Modernization | `go fix -diff ./...` | Advisory. A nonempty suggested diff exits nonzero. Review separately from a build failure. |
| Fuzz and benchmarks | Targeted `go test -fuzz` or `go test -bench` | Use where input risk or a performance claim warrants them. |

Use the [Go race detector requirements](https://go.dev/doc/articles/race_detector)
to validate runner support. When the new-project race default does not apply
because there are no runnable tests, record NOT TRIGGERED with evidence. A
project's existing binding race rule still governs its own checks. In every
Go project, flow step 8 also requires the race or hazard detector for work on
timing, concurrency or shared state. Use an allowed substitute when it meets
the requirement. If the required proof stays unavailable, record BLOCKED.
The [Go fix exit-code fixture](https://github.com/golang/go/blob/go1.27.4/src/cmd/go/testdata/script/fix_diff_exitcode.txt)
shows the exact diff distinction. Apply suggested edits only within authorized
scope. Staticcheck is third-party. Govulncheck is a Go ecosystem tool.
Tool dependencies added with `go get -tool` modify project manifests and follow
normal dependency authority. Reuse project runners without adding a Makefile
just for this policy. Retain each gate's own result, commands, revision and logs.

## Development and release builds

Use normal optimized Go builds and focused tests for development. If a
committed profile slows local builds, measure before choosing `-pgo=off` for
the development runner. Premerge uses the project's separate required gates.

Build one named main package per release. Adapt the example to the actual
package and output. Keep useful VCS metadata. Run the authorized binary
vulnerability check when available. If the project requires the check and it
cannot run, record BLOCKED.

```sh
go build -trimpath -pgo=auto -o bin/myservice ./cmd/myservice
go version -m bin/myservice
```

`-trimpath` removes local filesystem paths without establishing reproducibility
by itself. Consider `CGO_ENABLED=0` only for compatible dependencies and
runtime behavior. Use stripping only with accepted debug tradeoffs, PIE only
for supported targets and policy, and architecture tuning such as
`GOAMD64=v3` only after checking all deployment CPUs and measuring.
Use standard Go optimization. Avoid fictional `-O3` options, disabled bounds
checks via `-gcflags=-B`, debugger-style `-N -l`, blanket experiments, and
claims that a race-test binary is a performance release.

An initial release without a representative profile builds normally. Collect
genuine CPU pprof data from protected observability or a realistic load test.
Check for sensitive content and retain workload, source, date and hash. Keep
one `default.pgo` per intended main package. `-pgo=auto` can pick it up in
normal builds and affect dependencies and build time. Compare matched off
and auto builds for latency, throughput, CPU, memory, size and build time on
representative workloads and hardware. Keep or refresh profiles only with
measured benefit and acceptable costs. When passing an explicit profile path,
build each binary separately. Keep `/debug/pprof` private.
[Official Go PGO guide](https://go.dev/doc/pgo)

## Verify and roll back

Use task-owned fixtures for positive and negative setup, client operations,
loading, Go gates, version maintenance and rollback. Retain exact commands,
versions, outputs, environment and known gaps. Verify the installed framework
paths as well as the published source. Record platform, cloud or client
combinations you could not exercise as unverified.

Before considering Claude MCP as an adopted route, compare LSP only with
LSP plus MCP on the same representative Go tasks, checkpoints, model and
effort, with independent repeats. Check functional tests, reviewed defects,
missed edits and real semantic calls alongside tokens, wall time and machine
resources. Treat a small comparison as feasibility evidence. Keep the default
LSP-only when quality or resource benefit is unproven.

Record ownership and effective state before writes. On authorized rollback,
use native project-scope plugin uninstall with `--keep-data` where supported.
Remove only matching Flow-owned server entries, generated files,
and marked blocks. Compare with the recorded pre-setup settings. Remove a
leftover key or file only when setup owned it and no other changes are present.
Re-read current state and reconcile later edits. Preserve
other scopes, concurrent settings and user-level binaries and caches.
Keep before-and-after evidence and describe any retained shared cache.
