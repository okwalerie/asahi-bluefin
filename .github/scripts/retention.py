"""Plan GHCR retention; deletion and dependency handling belong to the cleanup action.

Keep everything for seven days, then the newest tagged build per ISO week
(Monday–Sunday UTC) until one calendar month ago. Channel tags stay protected.
"""
import calendar
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import subprocess

REFERRER_TAG = re.compile(r"sha256-[0-9a-f]{64}\..+")
DIGEST = re.compile(r"sha256:[0-9a-f]{64}")


def month_ago(now):
    year, month = (now.year, now.month - 1) if now.month > 1 else (now.year - 1, 12)
    return now.replace(year=year, month=month,
                       day=min(now.day, calendar.monthrange(year, month)[1]))


def retained_digests(versions, now):
    recent = now - timedelta(days=7)
    oldest = month_ago(now)
    keep = set()
    weeks = {}
    for version in versions:
        digest = version['name']
        if not DIGEST.fullmatch(digest):
            raise ValueError(f'Invalid image digest: {digest!r}')
        created = datetime.fromisoformat(version['created_at'].replace('Z', '+00:00'))
        if created.tzinfo is None:
            raise ValueError('Version timestamp must include timezone')
        created = created.astimezone(timezone.utc)
        tags = version['metadata']['container']['tags']
        if created >= recent:
            # Protect the exact boundary even if deletion starts seconds later.
            keep.add(digest)
        elif created >= oldest and any(not REFERRER_TAG.fullmatch(t) for t in tags):
            week = created.isocalendar()[:2]
            candidate = (created, digest)
            if candidate > weeks.get(week, (datetime.min.replace(tzinfo=timezone.utc), '')):
                weeks[week] = candidate
    keep.update(digest for _, digest in weeks.values())
    return keep, weeks


def main():
    # The API enumerates package versions, not registry tags, including all pages.
    pages = json.loads(subprocess.check_output([
        'gh', 'api', '--paginate', '--slurp',
        '/users/okwalerie/packages/container/asahi-bluefin/versions?per_page=100',
    ], text=True))
    versions = [version for page in pages for version in page]
    if not versions:
        raise ValueError('Empty package inventory; refusing cleanup')
    now = datetime.now(timezone.utc)
    keep, weeks = retained_digests(versions, now)
    print(f'Inventory: {len(versions)} versions; cutoff: {month_ago(now).isoformat()}')
    for week, (created, digest) in sorted(weeks.items()):
        print(f'Weekly archive {week}: {created.isoformat()} {digest}')
    exclusions = ','.join(['latest', '44', *sorted(keep)])
    with Path(os.environ['GITHUB_OUTPUT']).open('a') as output:
        output.write(f'exclude={exclusions}\n')


if __name__ == '__main__':
    main()
