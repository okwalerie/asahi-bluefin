from datetime import datetime, timedelta, timezone
import unittest
from retention import month_ago, retained_digests

NOW = datetime(2026, 10, 21, 12, tzinfo=timezone.utc)


def version(n, age, tags=None):
    return {
        'name': f'sha256:{n:064x}',
        'created_at': (NOW - timedelta(days=age)).isoformat(),
        'metadata': {'container': {'tags': tags if tags is not None else [f'build-{n}']}},
    }


class RetentionTests(unittest.TestCase):
    def test_all_recent_including_untagged_and_boundary(self):
        versions = [version(1, 0), version(2, 6, []), version(3, 7)]
        self.assertEqual(retained_digests(versions, NOW)[0], {v['name'] for v in versions})

    def test_newest_per_calendar_week(self):
        versions = [version(1, 8), version(2, 9), version(3, 15), version(4, 16),
                    version(5, 22), version(6, 23), version(7, 29), version(8, 30)]
        keep, weeks = retained_digests(versions, NOW)
        self.assertEqual(keep, {versions[i]['name'] for i in [0, 2, 4, 6]})
        self.assertEqual(len(weeks), 4)

    def test_month_boundary_inclusive(self):
        versions = [version(1, 30), version(2, 30.01), version(3, 40)]
        self.assertEqual(retained_digests(versions, NOW)[0], {versions[0]['name']})

    def test_signatures_and_untagged_are_not_weekly_builds(self):
        versions = [version(1, 8, []), version(2, 9, ['sha256-' + 'a' * 64 + '.sig']),
                    version(3, 10)]
        self.assertEqual(retained_digests(versions, NOW)[0], {versions[2]['name']})

    def test_order_independent_and_deterministic_ties(self):
        versions = [version(1, 8), version(2, 8), version(3, 15)]
        self.assertEqual(retained_digests(versions, NOW), retained_digests(versions[::-1], NOW))
        self.assertIn(versions[1]['name'], retained_digests(versions, NOW)[0])

    def test_calendar_month_clamps_and_handles_new_year(self):
        self.assertEqual(month_ago(datetime(2024, 3, 31, tzinfo=timezone.utc)).day, 29)
        self.assertEqual(month_ago(datetime(2025, 3, 31, tzinfo=timezone.utc)).day, 28)
        self.assertEqual(month_ago(datetime(2026, 1, 31, tzinfo=timezone.utc)),
                         datetime(2025, 12, 31, tzinfo=timezone.utc))

    def test_bad_inventory_fails_closed(self):
        bad = version(1, 8)
        bad['name'] = 'not-a-digest'
        with self.assertRaises(ValueError):
            retained_digests([bad], NOW)
        bad = version(1, 8)
        bad['created_at'] = '2026-10-13T12:00:00'
        with self.assertRaises(ValueError):
            retained_digests([bad], NOW)

    def test_iso_year_boundary(self):
        now = datetime(2027, 1, 10, 12, tzinfo=timezone.utc)
        versions = [version(1, 8), version(2, 9)]
        versions[0]['created_at'] = '2027-01-01T12:00:00Z'
        versions[1]['created_at'] = '2026-12-31T12:00:00Z'
        keep, weeks = retained_digests(versions, now)
        self.assertEqual(len(weeks), 1)
        self.assertEqual(keep, {versions[0]['name']})


if __name__ == '__main__':
    unittest.main()
