<p align="center">
  <img src="docs/images/banner.png" alt="tinypool-options-rce-check by CompleteTech LLC" width="100%">
</p>

<p align="center">
  <a href="https://github.com/CompleTetech-Security/tinypool-options-rce-check/actions"><img src="https://img.shields.io/github/actions/workflow/status/CompleTetech-Security/tinypool-options-rce-check/tests.yml?label=tests" alt="Tests"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-1E3A8A" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/dependencies-none-067647" alt="No runtime dependencies">
  <a href="LICENSING.md"><img src="https://img.shields.io/badge/license-AGPL--3.0%20%7C%20commercial-64748B" alt="AGPL-3.0 or commercial license"></a>
</p>

# tinypool-options-rce-check

Offline evidence checker for **CVE-2026-104849 — Tinypool worker-options prototype-pollution gadget** (alias GHSA-85c8-ppgw-ccpr).

It compares operator-reported `tinypool` versions with the reviewed advisory rules and writes CSV, JSON or HTML reports. It is version-evidence triage only: it never contacts websites, imports application code, runs a package manager, or executes exploit payloads, and exploitability is always reported as `not_tested`.

## Contents

- [Scope](#scope)
- [Requirements](#requirements)
- [Quick start](#quick-start)
- [Synthetic report preview](#synthetic-report-preview)
- [Reviewed rules](#reviewed-rules)
- [Interpreting results](#interpreting-results)
- [Preconditions](#preconditions)
- [Providing evidence](#providing-evidence)
- [Options](#options)
- [Reports and output](#reports-and-output)
- [Exit status and interruption](#exit-status-and-interruption)
- [Limitations](#limitations)
- [Sources and provenance](#sources-and-provenance)
- [Project documents](#project-documents)
- [Contributing and security](#contributing-and-security)
- [License and brand assets](#license-and-brand-assets)

## Scope

This repository covers only CVE-2026-104849. The checker does not scan deployed systems, fetch package inventories, analyze source code, or test exploitability. It reads versions and optional observations that you supply and reports what those claims imply under the reviewed rules.

A public URL cannot provide installed package inventory. Obtain each deployed package instance's exact version and provenance; declarations and local workstation versions are not deployment evidence. Use it only with inventories you are authorized to assess.

## Requirements

- Python 3.10 or newer, standard library only. No runtime dependencies and no network access.
- `tinypool_options_rce_check.py` can be copied and run on its own; no companion repository is needed at runtime.
- The CI workflow (`.github/workflows/tests.yml`) runs the local-only tests and `--help` on Python 3.10 and 3.14 on Ubuntu and Windows.

## Quick start

```sh
# Assess one reported version; the default format is csv
python tinypool_options_rce_check.py --version 2.1.2 --format json

# Assess a JSON inventory and save an HTML report to a new file
python tinypool_options_rce_check.py --inventory examples/inventory.example.json --format html --output report.html

# Assess a CSV list and exit 1 if any entry is potentially affected
python tinypool_options_rce_check.py --csv-list inventory.csv --fail-on-finding

# Show all options, then run the local tests
python tinypool_options_rce_check.py --help
python -m unittest -v
```

`examples/inventory.example.json` is a synthetic entry (`2.1.2`, label `example-package-instance`, all observations `null`). Without `--output`, the report goes to stdout.

## Synthetic report preview

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/images/report-dark.png">
  <img src="docs/images/report-light.png" alt="Tinypool synthetic report" width="100%">
</picture>

[Open the synthetic example report](docs/example-report.html). Example data only; this is not a live assessment.

## Reviewed rules

The primary advisory and reviewed database were retrieved on 2026-10-24 (`rules_as_of` in every report).

| Example reported version | Result |
| --- | --- |
| 2.0.9 | `potentially_affected` |
| 2.1.0 | `potentially_affected` |
| 2.1.1 | `unknown` |
| 2.1.2 | `fixed_version_reported` |
| 2.1.3 | `fixed_version_reported` |
| 2.2.0 | `unknown` |
| 3.0.0 | `unknown` |

- **Affected interval:** `0.0.0` through `2.1.0` inclusive.
- **Fixed line:** `2.1.x`, fixed in `2.1.2`. Future lines remain unknown rather than extrapolating a patch claim.
- **Disputed boundary:** `2.1.1`. The maintainer range (`<=2.1.0`) and the GitHub Reviewed range (`<2.1.2`) disagree there, so it is reported as `unknown` and never as clean. Obtain maintainer evidence.
- **Not the trigger:** `pool.run(task)` alone is not the documented trigger.
- **Severity:** the maintainer rates it High; the database rates it Critical. Retain provenance when reporting.

Only plain stable `MAJOR.MINOR.PATCH` versions are compared. A single leading `v` and surrounding ASCII whitespace are accepted.

## Interpreting results

| Status | Meaning |
| --- | --- |
| `potentially_affected` | The reported version is in the documented affected interval. This is not confirmed exploitability: preconditions and exploitability were not established. |
| `fixed_version_reported` | The reported version is at or above the fix within the reviewed `2.1.x` line. This describes a version claim only; it never attests an installed patch or safety. |
| `unknown` | Evidence is insufficient to classify. This is neither a clean result nor a finding. |

Every result retains `exploitability: not_tested`. `evidence_type` is `operator_reported_version`; `evidence_confidence` is `insufficient` for `unknown` and `low` otherwise.

Each result also carries a more specific `version_status`:

| `version_status` | Status | Cause |
| --- | --- | --- |
| `in_documented_affected_range` | `potentially_affected` | Version is within `0.0.0`–`2.1.0`. |
| `at_or_above_fixed_version` | `fixed_version_reported` | Version is `2.1.2` or later within `2.1.x`. |
| `source_discrepancy` | `unknown` | Version is `2.1.1`, where the sources disagree. |
| `outside_reviewed_range` | `unknown` | Version is outside the affected interval and the reviewed fixed line; no safety or other-vulnerability conclusion is made. |
| `vendor_build_unverified` | `unknown` | `build_source` is a custom or vendor build, which needs independent patch evidence. |
| `qualified_version_unverified` | `unknown` | Prerelease, nightly/rc or suffixed versions need vendor verification. |
| `unrecognized_or_partial_version` | `unknown` | Version text is malformed or partial. |
| `version_not_disclosed` | `unknown` | No version was reported. Missing metadata does not establish that the runtime is unaffected. |

Operational failures (bad arguments, unreadable or invalid input, output errors) are not assessment results. They exit with status 2 and are never reported as `unknown` or clean.

## Preconditions

The advisory describes conditions that must hold for the gadget to matter. You can record your own observations of them:

| Optional operator observation | Meaning |
| --- | --- |
| `caller_supplies_pool_run_options_object` | caller supplies pool.run options object |
| `options_lacks_an_own_filename_property` | options lacks an own filename property |
| `separate_prototype_pollution_primitive` | separate prototype-pollution primitive |
| `attacker_controlled_worker_module_available` | attacker-controlled worker module available |

Each observation is `true`, `false` or unset (`null` or blank). Reports show them as `reported_true`, `reported_false` or `not_reported`. They are unverified, and never change the package-version result. No source search, taint analysis, reachability test, or runtime evaluation is performed. Absent observations do not establish mitigation.

## Providing evidence

Provide at least one of `--version`, `--inventory` or `--csv-list`; they can be combined and repeated in one run.

**Command line.** `--version` (alias `--package-version`) is repeatable. Each value is a separate instance, not evidence reconciliation for a single instance. `--build-source` and the observation flags (the key with underscores turned into hyphens, such as `--separate-prototype-pollution-primitive true`) apply to every `--version` input.

**JSON inventory.** One object or an array of objects:

| Field | Required | Notes |
| --- | --- | --- |
| `schema_version` | yes | Integer `1`. |
| `package_version` | yes | String. |
| `package` | no | Must be `"tinypool"` if present. |
| `label` | no | Display name; defaults to `<file stem>:<position>`. |
| `build_source` | no | Provenance of the build. |
| observation keys | no | `true`, `false` or `null`. |

**CSV list.** A header row is required and must include `package_version`. Optional columns are `label`, `build_source` and the observation keys (`true`, `false` or blank). `schema_version` and `package` are not CSV columns.

**Build provenance.** `build_source` values `unknown` (the default), blank, `upstream`, `official` and `official_upstream` are compared as upstream builds. Any other value, such as a vendor name, yields `vendor_build_unverified` and `unknown`, because vendor and custom builds may backport fixes or differ from upstream.

**Rejected input.** Unknown or duplicate keys, wrong types, non-finite numbers and malformed JSON are rejected. CSV with duplicate or undocumented columns, rows with a different number of fields than the header, quotes inside unquoted cells, text after a closing quote, unterminated quotes, or NUL characters is rejected as well.

**Bounds.** Only regular UTF-8 files are accepted. Limits: 4 MiB per file, 100 files per run, 10,000 entries per run (including `--version` values) and 512 characters per text field. Work from stable copies; these checks are not a filesystem sandbox.

## Options

| Option | Description |
| --- | --- |
| `--version`, `--package-version` `VERSION` | Assess an explicitly supplied tinypool version offline; repeatable. |
| `--build-source SOURCE` | Provenance of the `--version` builds (default `unknown`, compared as upstream). |
| `--<observation-key>` `true\|false` | Observation applied to `--version` inputs; one flag per [precondition](#preconditions) key. |
| `--inventory FILE` | JSON object or array of entries; repeatable. |
| `--csv-list FILE` | CSV list with a `package_version` column; repeatable. |
| `--format csv\|json\|html` | Output format (default `csv`). |
| `--output PATH` | Save the report to a new file instead of stdout. |
| `--force` | Replace an existing output file explicitly. |
| `--brand NAME` | Organization name shown in the HTML report (default `CompleteTech LLC`, at most 512 characters). It has no other effect. |
| `--fail-on-finding` | Exit 1 when any result is `potentially_affected`. |
| `--tool-version` | Print the checker name and version, then exit. |

The detailed contract is in [docs/REFERENCE.md](docs/REFERENCE.md); `--help` shows the current options.

## Reports and output

JSON, formula-neutralized CSV and escaped, script-free HTML share the same assessments.

- **JSON:** an object with `tool`, `tool_version`, `generated_at`, `report_schema_version` (`"1.0"`), `cve`, `rules_as_of`, `sources`, `complete` and a `results` array.
- **CSV:** one `record_type=result` row per asset observation, with the result fields above, a `precondition_<key>` column for each observation, `report_schema_version`, `report_complete` and the run identity. Cells that could start a spreadsheet formula are prefixed with `'`, and all cells are quoted. NUL characters are rejected before a report is written. A zero-result report has one `record_type=summary` row carrying completeness, schema, rule date, CVE and `not_tested`; it is not an asset finding.
- **HTML:** a self-contained page with a restrictive content security policy, sorted with potentially affected results first. It shows the same generation time and checker identity, the fixed release, precondition observations, and notes. An interrupted run is flagged with a notice.

All formats preserve the same run identity: `tool`, `tool_version`, and ISO 8601 UTC `generated_at`. CSV repeats these fields on every result and empty summary. The CLI captures generation time once before assessment and retains it when interrupted. `rules_as_of` remains the advisory verification date; generation time is not evidence acquisition time or deployed-patch attestation.

**Safe publication.** The report is rendered fully in memory before anything is written. With `--output`, the directory must already exist and the file is staged then published atomically. An existing file is not overwritten unless you pass `--force`, and the output must differ from every input file even with `--force`. Without `--force`, publication uses a hard link; on a filesystem without hard links the checker reports an error and asks you to choose another filesystem or use `--force`.

**Privacy.** Reports contain operator data. Keep real targets, inventories and reports out of commits.

## Exit status and interruption

| Exit | Meaning |
| --- | --- |
| `0` | Run completed. |
| `1` | At least one result is `potentially_affected` and `--fail-on-finding` was given. |
| `2` | Argument, input or output error; nothing was assessed or the report was not written. |
| `130` | Interrupted. Completed observations are preserved when possible. |

`unknown` results do not trigger `--fail-on-finding` and are not a clean result.

On interruption (`130`):

- Before the output path is validated, nothing is written.
- If nothing has been published or started yet, completed results are written with `complete: false` (JSON), `report_complete=false` (CSV) or an interrupted-run notice (HTML). An empty interrupted CSV retains a summary row.
- If the complete report was already published, it is preserved, and the checker does not retry.
- If publication is left indeterminate, the checker does not retry. The diagnostic does not establish whether publication succeeded, so inspect the output before retrying.
- If interrupted while writing to stdout, the document can be truncated and no second report is appended.

## Limitations

- Results rest on operator-reported versions, not on observed deployments. `fixed_version_reported` is a reported fixed version, not a verified deployed patch.
- Backports, vendor builds, prereleases and custom builds cannot be resolved offline and stay `unknown`.
- Precondition observations are unverified and never change the version result.
- Versions outside the reviewed interval and fixed line are `unknown`; no conclusion about other flaws is made.
- The tool does not establish exploitability, reachability or production exposure.

## Sources and provenance

- <https://github.com/tinylibs/tinypool/security/advisories/GHSA-85c8-ppgw-ccpr>
- <https://github.com/advisories/GHSA-85c8-ppgw-ccpr>

Bounded input and reporting helpers are bundled from the reviewed Node.js checker at `74aa57ba5df05c34d17ae67912cd26ec2335201b`, with package-specific range comparison and the mixed-whitespace CSV fix.

## Project documents

- [Evidence and CLI reference](docs/REFERENCE.md)
- [Implementation status](docs/IMPLEMENTATION.md)
- [Synthetic example report](docs/example-report.html)
- [Repository instructions](AGENTS.md)
- [`advisory.json`](advisory.json): offline rule metadata
- [`SHA256SUMS`](SHA256SUMS): checksum for the checker script

## Contributing and security

Read [AGENTS.md](AGENTS.md) and [CONTRIBUTING.md](CONTRIBUTING.md) first. Before proposing a change, run `python -m unittest -v`, `python tinypool_options_rce_check.py --help` and `git diff --check`. Use synthetic evidence only, and never run application code or send exploit payloads. Report flaws in this project privately as described in [SECURITY.md](SECURITY.md).

## License and brand assets

Available under the GNU AGPL-3.0 ([LICENSE](LICENSE)) or a separate commercial license from CompleteTech LLC; see [LICENSING.md](LICENSING.md). Contributions are licensed as described in [CONTRIBUTING.md](CONTRIBUTING.md#licensing-of-contributions).

CompleteTech LLC names, logos and the artwork in `docs/images/` are brand assets and are not licensed under the AGPL-3.0 or a commercial code license; see [BRAND_ASSETS.md](BRAND_ASSETS.md).
