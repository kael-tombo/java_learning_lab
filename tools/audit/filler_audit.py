#!/usr/bin/env python3
"""Detect templated filler in the lab documentation.

WHY: file-existence and non-empty checks cannot tell real content from placeholder text.
A line of genuine, lab-specific prose is very unlikely to appear verbatim in many
unrelated labs. This tool finds prose that does.

METHOD (content-agnostic; it needs no list of known filler phrases):
  1. For every markdown file, take *prose lines*: >=25 chars, >=5 words, outside code
     fences, not headings, not table rows, not ending in ; { }.
  2. Normalise (lower-case, collapse whitespace, digits -> '#').
  3. A line is FILLER if it appears in >= MIN_DIRS distinct lab directories.
  4. A file is FILLER-HEAVY if it has >= 5 filler lines making up >= 25% of its prose
     lines, or it contains the generator stub snippet `/* resource goes here */`.

LIMITS: deliberately conservative. Templated text with the topic name swapped in is NOT
caught (the lines differ), so the true share of filler is higher than reported. Code is
excluded because idiomatic code legitimately repeats.

USAGE (from the repository root):
    python tools/audit/filler_audit.py            # prints a summary, writes the CSV
"""
import csv
import os
import re
import sys
from collections import Counter, defaultdict

MIN_DIRS = 20
ROOT = 'labs'
OUT = os.path.join('tools', 'audit', 'filler_heavy_files.csv')
DIGITS = re.compile(r'\d+')
STUB = re.compile(r'resource goes here')


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


def prose_lines(text):
    in_code = False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith('```'):
            in_code = not in_code
            continue
        if not in_code and is_prose(s):
            yield norm(s)


def main():
    docs = []
    line_dirs = defaultdict(set)
    for dirpath, _dirs, names in os.walk(ROOT):
        for name in names:
            if not name.endswith('.md'):
                continue
            path = os.path.join(dirpath, name)
            try:
                text = open(path, encoding='utf-8', errors='ignore').read()
            except OSError:
                continue
            lines = list(prose_lines(text))
            for n in set(lines):
                line_dirs[n].add(dirpath)
            docs.append((path, lines, len(STUB.findall(text))))

    filler_set = {n for n, ds in line_dirs.items() if len(ds) >= MIN_DIRS}
    heavy = []
    for path, lines, stub in docs:
        filler = sum(1 for n in lines if n in filler_set)
        pct = filler / len(lines) if lines else 0.0
        if (filler >= 5 and pct >= 0.25) or stub >= 2:
            heavy.append((path, len(lines), filler, round(100 * pct), stub))
    heavy.sort(key=lambda r: (-r[3], r[0]))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['file', 'prose_lines', 'filler_lines', 'filler_pct', 'stub_blocks'])
        for path, prose, filler, pct, stub in heavy:
            w.writerow([path.replace('\\', '/'), prose, filler, pct, stub])

    print('files scanned          : %d' % len(docs))
    print('distinct filler lines  : %d (each seen in >= %d lab dirs)' % (len(filler_set), MIN_DIRS))
    print('filler-heavy files     : %d (%.1f%%)' % (len(heavy), 100.0 * len(heavy) / max(1, len(docs))))
    by_acad = Counter(os.path.relpath(p, ROOT).split(os.sep)[0] for p, *_ in heavy)
    print('by academy             :', dict(by_acad.most_common(10)))
    print('manifest written to    : %s' % OUT)


if __name__ == '__main__':
    sys.exit(main())