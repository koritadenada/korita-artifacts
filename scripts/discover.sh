#!/usr/bin/env bash
# List Pages-enabled repos and their HTML files, flagging any not yet in artifacts.json.
set -euo pipefail
OWNER=koritadenada
cd "$(dirname "$0")/.."
gh api "users/$OWNER/repos?per_page=100" --jq '.[] | select(.has_pages) | .name' | while read -r r; do
  [ "$r" = korita-artifacts ] && continue
  src=$(gh api "repos/$OWNER/$r/pages" --jq '.source.path' | sed 's#^/##')
  grep -q "\"repo\": \"$r\"" artifacts.json && flag="" || flag="  <-- NEW SITE"
  echo "== $r$flag"
  gh api "repos/$OWNER/$r/git/trees/HEAD?recursive=1" --jq '.tree[] | select(.type=="blob") | .path' \
    | grep -E '\.html$' | grep -v '_template\.html$' | { [ -n "$src" ] && grep "^$src/" | sed "s#^$src/##" || cat; } | sed 's/^/   /'
done
