#!/usr/bin/env bash
# Rebuild the static site and push it to the gh-pages branch (GitHub Pages).
# Usage: ./publish.sh            (run after: .venv/bin/python update.py)
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python; [ -x "$PY" ] || PY=python3
$PY build_site.py
touch site/.nojekyll
REMOTE=$(git remote get-url origin)
WORK=.gh-pages-work
rm -rf "$WORK"; mkdir -p "$WORK"
cp -a site/. "$WORK"/
cd "$WORK"
git init -q -b gh-pages
git config user.name "smith83975-sys"
git config user.email "342546096+smith83975-sys@users.noreply.github.com"
git add -A
git commit -q -m "Publish site $(date -u +%Y-%m-%dT%H:%MZ)"
git push -q -f "$REMOTE" gh-pages
cd .. && rm -rf "$WORK"
echo "Published: https://smith83975-sys.github.io/metalfundcompare/"
