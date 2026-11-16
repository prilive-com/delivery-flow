# Headroom offline study

This is Experiment D1, measured on Linux x86_64 on 2026-11-16 with
[headroom-ai 0.44.0](https://github.com/headroomlabs-ai/headroom/releases/tag/v0.44.0). It is research, not a live integration. Headroom stays out
of normal Delivery Flow setup. The study did not wrap an agent or mandatory reviewer.
No quality-critical evidence was lossy-compressed. Full originals were retained.

## What ran

The actual release's Python library processed six saved synthetic fixtures:
repeated nested JSON with an important outlier, a failing test and chained
stack trace, numbered source, numbered requirements, clean logs and prose.
Two strict arms covered every fixture. A constrained coding arm used only
noncritical logs and prose. Separate direct-codec controls covered two JSON
shapes. A fresh offline dependency rebuild reproduced all 48 payload outputs.
The same lock and all originals/results remain in private retained evidence.

The native jobs had a 4 GiB memory ceiling and a 200% CPU quota. The measured largest
install/rebuild charge was 649,437,184 bytes; no OOM was recorded. The kernel filter denies non-UNIX socket creation, connect, sendto, sendmsg
and sendmmsg. Captured traces show blocked Internet socket and connect attempts.
No send-family call was recorded, so those denials were not exercised by the traces. Public package/tokenizer downloads happened beforehand.
This tested machine is not proof of Windows/macOS or hostile-code isolation.

## What the numbers mean

Counts below use tiktoken 0.14.0, o200k_base on tool payloads. They are local
text counts, not provider bills, cache hits, model answers or whole-task savings.

| Case | Before tokens | After tokens | Meaning |
|---|---:|---:|---|
| Clean logs, safe router |12240|760| Changed encoding; inverse restored every byte. |
| Nested JSON, safe router |24494|24494| Passed through unchanged. |
| Nested JSON, direct strict codec |24494|7737| Table encoding; decoded keys/types/values and outlier matched. |
| Flat JSON, direct strict codec |14405|4591| Table encoding; decoded keys/types/values and outlier matched. |
| Failing test, numbered source/requirements and prose | unchanged | unchanged | Byte identity held for these samples only. |

The direct codec is a different supported API from the router. Its table
encoding is not the original JSON-array form. A decoder preserving data does
not prove that a model will interpret that encoding equally well. The failing
test sample was below the router's error-protection cap; larger errors, ANSI
and patch formats were not certified. Keep exact critical bytes protected.

## API limits and decision

The [0.44.0 configuration](https://github.com/headroomlabs-ai/headroom/blob/v0.44.0/headroom/config.py) has no LOSSLESS/CODING compression-enum pair. The [savings-profile lookup](https://github.com/headroomlabs-ai/headroom/blob/v0.44.0/headroom/agent_savings.py) resolves CODING to
a savings profile; LOSSLESS used as a profile warns and falls back to coding.
The study used verified explicit lossless settings and read-only learning
policy. Its constrained coding arms are not unrestricted stock coding.
An unrestricted two-mode comparison therefore remains UNAVAILABLE.

The study found possible offline log/data compression. It did not establish a safe default
for agents. Real answer quality, mandatory-review isolation, provider caching,
usage and total operational cost remain untested. Live adoption is NO-GO.
D2/D3 need their separate staged decision and quality proof. No automatic
learning, instruction rewriting, cross-agent memory, provider routing,
proxy, MCP registration or default loader change is installed.

Use the [full flow](../DELIVERY-FLOW.md) and existing optional-tool rules.
This study adds no required tool, installer or gate. Reverting this report
removes only documentation; there is no live Headroom deployment to undo.
