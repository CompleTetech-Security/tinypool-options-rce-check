# tinypool-options-rce-check

**Tinypool worker-options prototype-pollution gadget**  
By [CompleteTech LLC](https://complete.tech)

> **Repository initialized; checker implementation pending.**
> This project currently contains research and an implementation checklist.
> It does not assess systems or provide an executable detection rule.

## One exploit, one repository

| Field | Scope |
| --- | --- |
| Exploit identifier | `CVE-2026-104849` |
| Aliases for this same exploit | `GHSA-85c8-ppgw-ccpr` |
| Research verification date | 2026-10-23 |
| Implementation state | `planned` |
| Detection rule | **Disabled — research only** |

This repository is dedicated to **CVE-2026-104849**. Aliases and multiple affected
products identify this same exploit; they do not create additional scanner scopes.
Future fixes for different vulnerabilities belong in independent repositories.

## Advisory snapshot

The following is source-backed research for implementation planning. It is not a
test result, a live rule feed, or an attestation that a deployed system is patched.

### Affected versions or conditions

<=2.1.0 (maintainer); <2.1.2 (GitHub Reviewed)

### Reported fixes or remediation

2.1.2

### Deployment preconditions to establish

- caller supplies pool.run options object
- options lacks an own filename property
- separate prototype-pollution primitive
- attacker-controlled worker module available

### Evidence notes and limitations

- pool.run(task) alone is not the documented trigger. Surface 2.1.1 source conflict and do not report clean. Maintainer severity High differs from database Critical; retain provenance.

## Planned checker behavior

The intended checker follows the evidence and reporting conventions of
[node2shell-check](https://github.com/CompleteTech-LLC/node2shell-check) and [php2shell-check](https://github.com/CompleteTech-LLC/php2shell-check):

- Prefer offline version, inventory, or configuration evidence appropriate to this exploit.
- Keep version state, documented preconditions, evidence provenance, and uncertainty separate.
- Preserve `exploitability: not_tested`; never run exploit payloads or confirm compromise.
- Keep missing, malformed, conflicting, vendor-qualified, prerelease, and uncovered versions `unknown`.
- Produce human-readable findings and machine-readable JSON/CSV; document each output before release.
- Add bounded, explicitly selected passive network behavior only if it provides useful evidence.

These capabilities are **planned**, not implemented. There are currently no
checker commands, downloadable binaries, test results, or CI claims.

## Start here

1. Review [advisory.json](advisory.json) and the primary sources below.
2. Work through the exploit-specific [implementation checklist](docs/IMPLEMENTATION.md).
3. Read [AGENTS.md](AGENTS.md), [CONTRIBUTING.md](CONTRIBUTING.md), and
   [SECURITY.md](SECURITY.md) before contributing.

## Primary sources

1. [github.com](https://github.com/tinylibs/tinypool/security/advisories/GHSA-85c8-ppgw-ccpr)
2. [github.com](https://github.com/advisories/GHSA-85c8-ppgw-ccpr)

The research date records the supplied verification snapshot. Recheck primary
advisories before enabling any detection logic, and retain contradictory evidence.

## License

[AGPL-3.0](LICENSE), or a separate commercial agreement with CompleteTech LLC.
See [LICENSING.md](LICENSING.md) and the
[contribution terms](CONTRIBUTING.md#licensing-of-contributions).
Names and branding are governed by [BRAND_ASSETS.md](BRAND_ASSETS.md).

Copyright © 2026 CompleteTech LLC.
