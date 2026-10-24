# tinypool-options-rce-check

Offline evidence checker for **CVE-2026-104849 — Tinypool worker-options prototype-pollution gadget**. Python 3.10+, standard library only. The executable can be copied alone. It never contacts websites, imports application code, runs a package manager, or executes exploit payloads.

```sh
python tinypool_options_rce_check.py --version 2.1.2 --format json
python tinypool_options_rce_check.py --inventory examples/inventory.example.json --format html --output report.html
python tinypool_options_rce_check.py --csv-list inventory.csv --fail-on-finding
python tinypool_options_rce_check.py --help
python -m unittest -v
```

## Reviewed rules

Primary advisory and reviewed database retrieved 2026-10-24. A public URL cannot provide installed package inventory. Obtain each deployed package instance's exact version and provenance; declarations and local workstation versions are not deployment evidence.

| Example reported version | Result |
| --- | --- |
| 2.0.9 | `potentially_affected` |
| 2.1.0 | `potentially_affected` |
| 2.1.1 | `unknown` |
| 2.1.2 | `fixed_version_reported` |
| 2.1.3 | `fixed_version_reported` |
| 2.2.0 | `unknown` |
| 3.0.0 | `unknown` |

pool.run(task) alone is not the documented trigger. Surface 2.1.1 source conflict and do not report clean. Maintainer severity High differs from database Critical; retain provenance.

The reviewed fixed line is `2.1.x`; future lines remain unknown rather than extrapolating a patch claim. Versions outside the exact affected interval remain unknown, including older releases that might have other flaws. Missing, conflicting, malformed, prerelease, qualified, custom/vendor builds remain unknown. `fixed_version_reported` only describes a version claim; it never attests installed patches or safety. `potentially_affected` is not confirmed exploitability. Every row retains `exploitability: not_tested`.

## Preconditions

| Optional operator observation | Meaning |
| --- | --- |
| `caller_supplies_pool_run_options_object` | caller supplies pool.run options object |
| `options_lacks_an_own_filename_property` | options lacks an own filename property |
| `separate_prototype_pollution_primitive` | separate prototype-pollution primitive |
| `attacker_controlled_worker_module_available` | attacker-controlled worker module available |

Each observation is boolean or null, is unverified, and never changes the package-version result. No source search, taint analysis, reachability test, or runtime evaluation is performed. Absent observations do not establish mitigation.

## Evidence and reports

JSON accepts one object or an array of objects. Required: integer `schema_version: 1`, string `package_version`. Optional: `package: "tinypool"`, `label`, `build_source`, and the observation keys above. Unknown or duplicate keys, wrong types, non-finite numbers and malformed inputs are rejected. CSV requires `package_version`; optional columns are label, build_source, and observation keys (`true`, `false`, blank). CLI `--version` is repeatable; values are separate instances, not evidence reconciliation for a single instance. `--build-source` and observation flags (underscore becomes hyphen) apply to CLI versions.

Only regular UTF-8 input files are accepted. Limits: 4 MiB/file, 100 files, 10,000 entries total, 512 characters/text field. Work from stable copies; checks are not a filesystem sandbox. JSON, formula-neutralized CSV and escaped script-free HTML share assessments. Output files publish atomically and do not overwrite existing files without `--force`; inputs remain protected even with force.

Exit 0: completed run; 1: potentially affected with `--fail-on-finding`; 2: argument/input/output error; 130: interrupted, preserving completed observations when possible. Interruption during stdout can leave a truncated document and never appends a second report. Unknown does not count as a finding-gate failure or as a clean result. Reports contain operator data; keep real targets, inventories and reports out of commits.

## Sources and delivery

- https://github.com/tinylibs/tinypool/security/advisories/GHSA-85c8-ppgw-ccpr
- https://github.com/advisories/GHSA-85c8-ppgw-ccpr

[Synthetic report](docs/example-report.html), [reference](docs/REFERENCE.md), [implementation status](docs/IMPLEMENTATION.md), [AGENTS](AGENTS.md), [contribution terms](CONTRIBUTING.md), [security policy](SECURITY.md), [license](LICENSE), [dual licensing](LICENSING.md). Bounded input and reporting helpers are bundled from the reviewed Node.js checker at `74aa57ba5df05c34d17ae67912cd26ec2335201b`, with package-specific range comparison and the mixed-whitespace CSV fix. No companion repository is needed at runtime.

CSV `record_type=result` rows are asset observations. A zero-result report has a `record_type=summary` row carrying completeness, schema, rule date, CVE and `not_tested`; it is not an asset finding.

CSV rejects NUL characters before writing a report. An interruption after a complete report is published preserves that report and exits 130.
