# Resource use and optional work storage

This guide supplies a small capability procedure for Delivery Flow. The common flow sets quality, evidence and cleanup rules. A machine/project profile names the available commands and storage. This procedure adds no required OS, container product, extra disk, configuration parser or background service. The project's own platform requirements still apply.

## Discover once; recheck what can change

Record these facts in the existing step1 profile:

- The tested project runner and its actual execution domain: local host, VM/container or remote host; native and helper/daemon jobs it covers; combined and per-job controls and metric meanings. An executable on PATH proves neither readiness nor suitability.
- The shared capacity/admission procedure, job envelope, outside workloads and host reserve. Reuse existing coordination; a lock covers only processes that take it. Do not assume Linux flock coordinates native Windows work. Use one verified admission domain or separate pools whose totals and outside work fit the host. Start with one heavy job at a time where that coordination covers the work. A free-memory check is not a reservation.
- The optional preferred work root, expected volume identity and allowed ordinary disk fallback; actual filesystem/capacity/private access. Unconfigured extra storage uses the normal disk-backed path. Do not assume a drive letter or directory proves the expected device is mounted.
- The durable evidence root, disk reserve, task ownership/end condition and existing native cache policy. These are entries in the current profile, not a second state database.

## Select a compatible existing runner

| Environment | Suitable existing capability when present | Required distinction |
|---|---|---|
| Linux | Native group controls such as cgroup v2/systemd, tested container/VM/CI | Per-job versus shared cap; daemon-created work must be enrolled or separately budgeted. |
| Native Windows | A tested runner using Job Objects, or compatible bounded container/CI | Job commitment differs from Linux memory accounting. A PowerShell job is not proof of a Job Object limit. |
| Windows with WSL2 | The existing Linux workflow plus verified guest controls and host VM budget | WSL VM settings do not limit every job or native Windows tool. Count actual shared/separate VMs and host work once. |
| macOS/other | Tested native capability, otherwise compatible existing bounded VM/container/CI | Do not invent a tree-memory guarantee for launchd, nice or per-process limits. |

Reuse the current project recipe first. Choose Docker when available, ready and compatible with every required project surface; it is optional. Verify daemon location, image OS/architecture, mounts, auth/network and full commands. A Windows-native gate cannot be replaced with a different Linux test to fit Docker. The Docker client, Compose/SDK helpers, builder and remote daemon may have different limits/storage domains.

Label protection verified, documented-but-untested or unavailable. The baseline admission/storage discipline remains usable without a hard-cap provider; known risky work needs a safe configured route. Missing a particular product alone is not a new blocker. Preserve the flow's existing real-blocker and authority rules. Do not install a new framework or change machine permissions merely to follow this guide.

## Optional work volume

Prefer an approved available work root after validating its volume identity, filesystem semantics, private access and free capacity. Keep paths outside tracked source/frozen inputs unless the project's recipe explicitly needs otherwise. A simple layout is enough:

```
<work_root>/tasks/<project>/<unique-task-attempt>/
<work_root>/caches/<tool>/<environment>/   # only supported native cache reuse
<evidence_root>/<project>/<task>/        # durable, outside disposable eviction
```

Selecting a root alone does not redirect tools. Use their supported cache/temp settings for this job and explicit compatible container mounts. Preserve the project's source, HOME/auth and SDK paths; do not change global settings as a side effect. Keep native Windows, WSL/Linux and other build environments distinct; respect the tool's cache keys and limitations. A cache hit cannot replace a gate that requires a fresh run. Reuse private working data during a task; shared caches need their own documented policy and must not be globally cleared by task cleanup.

No extra disk: use the normal disk-backed work path. A configured preferred volume missing/full/wrong: wait or select only an allowed freshly checked fallback for a new job, record it, and prevent accidental writes through a missing mountpoint onto the system drive. Do not guess a device by size, auto-format it, move a running/frozen task or migrate Docker/VM/distro storage as a side effect. Provision once under existing authority; ordinary jobs do not ask again.

Use actual available bytes, filesystem allocation limits (such as available inodes/file records), admitted remaining growth and a configured reserve for each affected filesystem, including evidence storage. Do not promise a hard quota from monitoring alone. In a VM/VHD, check physical host backing space as well as guest free space. A remote Docker bind source belongs to its daemon host; validate mapping. Prefer the executing environment's compatible filesystem, not one universal path or format.

## Run, record and finish

Admit complete heavy work before launch. Queue or use an approved sufficient runner when it cannot fit. Normal children reuse the admitted envelope without self-deadlocking on a second lease. Track real helper/daemon boundaries. Keep every required test, selected model/effort, review round, full access/context/output and original evidence. Caps are emergency protection; a normal-work resource failure is not a successful optimization.

Reuse the existing run record for job/owner/source/command, execution domain and limits, storage identity/paths, start/end, actual exit, metric source/completeness, full logs and cleanup. Keep commitment, kernel charges, RSS, sampled and cached values distinct. A lost or falsely low metric is not zero. An outer failed/killed check is not green; deliberate negative tests must explicitly verify their expected behavior under the existing rules.

At completion, interruption or deployment wait, save and verify required context/evidence on durable storage; safely release idle RAM-backed scratch. Remove only no-longer-needed owned private work after current-use checks. Keep live data, required products, source, sessions, shared caches and evidence. No age-only sweep, global prune or hidden evidence-retention period. Cleanup errors stay visible.

Before adoption, run the same complete workload and quality checks with/without the optional disk and on each claimed environment. Include missing/full/wrong volume, concurrency/domain boundaries, cancellation, metric failure, cold/warm caches and preserved evidence. No normal-work resource OOM, added incomplete review or lost proof is accepted. Roll back to a verified recipe for new jobs; do not reduce quality or silently run unsafe heavy work unbounded.

The checks must reject a missing/wrong volume without new bytes behind its path, a Linux-only lock claimed to cover native Windows, WSL2 controls claimed for WSL1, and exhausted filesystem allocation despite free bytes. Check that the edited rules and guide exist in each installed location the agent actually loads. For an installation with a copied CLAUDE.md FLOW region, update the installed TOOLING/guide as well as DELIVERY-FLOW, then use its existing sync and verify the loaded copies. Other machines use their existing loader procedure. This guide does not port or require the optional Linux-only dflow reader.

## Primary references

- [Windows Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects), [commitment and peak fields](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information).
- [WSL VM settings](https://learn.microsoft.com/en-us/windows/wsl/wsl-config), [filesystem guidance](https://learn.microsoft.com/en-us/windows/wsl/filesystems), [host and VHD space](https://learn.microsoft.com/en-us/windows/wsl/disk-space).
- [Docker limits](https://docs.docker.com/engine/containers/resource_constraints/), [Desktop VM settings](https://docs.docker.com/desktop/settings-and-maintenance/settings/), [daemon-side bind mounts](https://docs.docker.com/engine/storage/bind-mounts/).
- [Linux cgroups](https://docs.kernel.org/6.8/admin-guide/cgroup-v2.html), [systemd example provider](https://www.freedesktop.org/software/systemd/man/255/systemd.resource-control.html).

These document capabilities; they do not certify a machine or supply a cross-platform runner. Record installed versions and verify the relevant behavior before claiming enforcement.
