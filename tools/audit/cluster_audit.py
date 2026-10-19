#!/usr/bin/env python3
"""Find audit-BLIND template clusters.

filler_audit.py pools prose lines seen in >= 20 lab directories; a template
cluster shared by only 5-19 labs is invisible to it (the legacy math labs keep
~322 identical lines per file this way).  This tool pools by *top lab dir*
(first path segment under labs/<academy>/...) and reports lines seen in
[CLUSTER_MIN, MIN_DIRS) distinct top labs plus per-lab rollups.

Content-agnostic, like filler_audit.py. Writes a CSV summary next to itself.
"""
import csv
import os
import re
import sys
from collections import defaultdict

MIN_DIRS = 20          # must match tools/audit/filler_audit.py
CLUSTER_MIN = 5
DIGITS = re.compile(r'\d+')


def is_prose(s):
    if len(s) < 25 or len(s.split()) < 5:
        return False
    if s.startswith(('#', '|', '```')):
        return False
    if re.search(r'[{};]\s*$', s):
        return False
    return bool(re.search(r'[a-zA-Z]{3,}', s))


def norm(s):
    return DIGITS.sub('#', re.sub(r'\s+', ' ', s.lower()))


def docs():
    for dirpath, _dirs, names in os.walk(ROOT := 'labs'):
        for name in names:
            if not name.endswith('.md'):
                continue
            path = os.path.join(dirpath, name)
            try:
                text = open(path, encoding='utf-8', errors='ignore').read()
            except OSError:
                continue
            rel = os.path.relpath(path, ROOT)
            parts = re.split(r'[\\/]', rel)
            top_lab = '/'.join(parts[:2]) if len(parts) >= 3 else '/'.join(parts[:1])
            yield path, rel, top_lab, text


def main():
    line_labs = defaultdict(set)
    lab_hits = defaultdict(set)
    for path, rel, top_lab, text in docs():
        seen = set()
        for line in text.splitlines():
            s = line.strip()
            if s and is_prose(s) and not s.startswith('```'):
                seen.add(norm(s))
        for n in seen:
            line_labs[n].add(top_lab)
            lab_hits[top_lab].add(n)
    clusters = {n: labs for n, labs in line_labs.items()
                if CLUSTER_MIN <= len(labs) < MIN_DIRS}
    per_lab = defaultdict(int)
    for n, labs in clusters.items():
        for l in labs:
            per_lab[l] += 1
    heavy = {k: v for k, v in per_lab.items() if v >= 5}
    by_acad = defaultdict(int)
    for lab in heavy:
        by_acad[lab.split('/')[0]] += 1
    print('cluster lines (shared by %d-%d labs): %d' % (CLUSTER_MIN, MIN_DIRS - 1,
                                                        len(clusters)))
    print('labs carrying >= 5 cluster lines: %d' % len(heavy))
    print('by academy:', dict(sorted(by_acad.items(), key=lambda kv: -kv[1])[:12]))
    for lab, c in sorted(heavy.items(), key=lambda kv: -kv[1])[:20]:
        print('   %4d | %s' % (c, lab))
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, 'cluster_labs.csv')
    with open(out, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['lab', 'cluster_lines'])
        for lab, c in sorted(heavy.items(), key=lambda kv: -kv[1]):
            w.writerow([lab.replace('\\', '/'), c])
    print('manifest written to   : %s' % out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
