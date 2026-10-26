"""Offline regressions for detached exports and interrupted run identity."""
import contextlib
import csv
from datetime import datetime, timezone
import io
import json
import socket
import unittest
from unittest import mock

import tinypool_options_rce_check as checker


STAMP = datetime(2026, 10, 25, 12, 34, 56, tzinfo=timezone.utc)


class ProvenanceTests(unittest.TestCase):
    def verify_export(self, text, fmt, *, count, complete):
        if fmt == 'csv':
            rows = list(csv.DictReader(io.StringIO(text, newline='')))
            self.assertEqual(max(1, count), len(rows))
            for row in rows:
                self.assertEqual(checker.TOOL_NAME, row['tool'])
                self.assertEqual(checker.TOOL_VERSION, row['tool_version'])
                self.assertEqual(STAMP.isoformat(), row['generated_at'])
                self.assertEqual(checker.RULES_DATE, row['rules_as_of'])
                self.assertEqual(str(complete).lower(), row['report_complete'])
                self.assertEqual('not_tested', row['exploitability'])
                self.assertEqual('result' if count else 'summary', row['record_type'])
            return [r['status'] for r in rows] if count else []
        if fmt == 'json':
            report = json.loads(text)
            self.assertEqual(checker.TOOL_NAME, report['tool'])
            self.assertEqual(checker.TOOL_VERSION, report['tool_version'])
            self.assertEqual(STAMP.isoformat(), report['generated_at'])
            self.assertEqual(checker.RULES_DATE, report['rules_as_of'])
            self.assertEqual(complete, report['complete'])
            self.assertEqual(count, len(report['results']))
            return [r['status'] for r in report['results']]
        self.assertIn(STAMP.isoformat(), text)
        self.assertIn(checker.TOOL_NAME + ' ' + checker.TOOL_VERSION, text)
        self.assertIn('rules as of ' + checker.RULES_DATE, text)
        if not complete:
            self.assertIn('Interrupted run.', text)

    def test_complete_and_empty_exports_share_captured_metadata(self):
        results = [checker.assess_entry('synthetic', 'version', v) for v in ('2.1.0', '2.1.1', '2.1.2')]
        for rows in (results, []):
            for fmt in ('csv', 'json', 'html'):
                with self.subTest(count=len(rows), fmt=fmt), mock.patch.object(checker, 'datetime') as clock:
                    clock.now.return_value = STAMP
                    out = io.StringIO()
                    checker.write_report(out, rows, format=fmt)
                    clock.now.assert_called_once_with(timezone.utc)
                    statuses = self.verify_export(out.getvalue(), fmt, count=len(rows), complete=True)
                    if statuses:
                        self.assertEqual(['potentially_affected', 'unknown', 'fixed_version_reported'], statuses)

    def test_interrupted_cli_preserves_start_time_and_completed_rows(self):
        real = checker.assess_entry
        for completed in (0, 1):
            for fmt in ('csv', 'json', 'html'):
                calls = 0
                def assess(*args, **kwargs):
                    nonlocal calls
                    calls += 1
                    if calls > completed:
                        raise KeyboardInterrupt
                    return real(*args, **kwargs)
                out = io.StringIO()
                with self.subTest(completed=completed, fmt=fmt), mock.patch.object(checker, 'datetime') as clock, mock.patch.object(checker, 'assess_entry', side_effect=assess), mock.patch.object(socket, 'socket', side_effect=AssertionError('offline only')), contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                    clock.now.return_value = STAMP
                    self.assertEqual(130, checker.main(['--version', '2.1.1', '--version', '2.1.2', '--format', fmt]))
                    clock.now.assert_called_once_with(timezone.utc)
                    statuses = self.verify_export(out.getvalue(), fmt, count=completed, complete=False)
                    if statuses:
                        self.assertEqual(['unknown'], statuses)

    def test_injected_timestamp_is_shared_without_reading_clock(self):
        for fmt in ('csv', 'json', 'html'):
            with mock.patch.object(checker, 'datetime') as clock:
                out = io.StringIO()
                checker.write_report(out, [], format=fmt, generated_at=STAMP.isoformat(), complete=False)
                clock.now.assert_not_called()
                self.verify_export(out.getvalue(), fmt, count=0, complete=False)

    def test_csv_row_cannot_override_run_identity(self):
        row = checker.assess_entry('synthetic', 'version', '2.1.1')
        row.update(tool='other', tool_version='other', generated_at='other')
        out = io.StringIO()
        checker.write_report(out, [row], generated_at=STAMP.isoformat())
        self.verify_export(out.getvalue(), 'csv', count=1, complete=True)


if __name__ == '__main__':
    unittest.main()
