#!/usr/bin/env python3
"""Check that optional app RPMs can own their repository files.

ChatGPT 26.1106.51428-1.aarch64 owns /etc/yum.repos.d/chatgpt.repo
and /etc/pki/rpm-gpg/RPM-GPG-KEY-chatgpt*. Image-owned copies block
rpm-ostree overlay checkout. Run from the repository root.
"""
from pathlib import Path
import yaml

root = Path(__file__).resolve().parents[1]
recipe = yaml.safe_load((root / 'recipes/recipe.yml').read_text())
owned = set()
for module in recipe['modules']:
    if module['type'] != 'files':
        continue
    for mapping in module['files']:
        source = root / 'files' / mapping['source']
        destination = Path(mapping['destination'])
        for source_file in source.rglob('*'):
            if source_file.is_file():
                owned.add(str(destination / source_file.relative_to(source)))

conflicts = {p for p in owned if p == '/etc/yum.repos.d/chatgpt.repo'
             or p.startswith('/etc/pki/rpm-gpg/RPM-GPG-KEY-chatgpt')}
assert not conflicts, f'Image conflicts with ChatGPT RPM: {sorted(conflicts)}'
assert '/usr/share/asahi-bluefin/bootstrap/chatgpt.repo' in owned
assert '/etc/yum.repos.d/claude-desktop-extra.repo' in owned
print('Optional-app repository ownership checks passed')
