# korita-artifacts

One page that links every artifact published on GitHub Pages under `koritadenada`, grouped by site, with thumbnails, search and tag filters.

Live: https://koritadenada.github.io/korita-artifacts/

## Layout

| Path | What |
|---|---|
| `artifacts.json` | The manifest: one collection per Pages site, one entry per page |
| `scripts/build.py` | Renders `docs/index.html` from the manifest (dates from `gh api`; `--no-dates` to skip) |
| `scripts/thumbs.sh` | Re-captures `docs/thumbs/*.jpg` with headless Chrome (macOS) |
| `scripts/discover.sh` | Lists Pages-enabled repos and their HTML pages, flags sites missing from the manifest |
| `docs/` | GitHub Pages source (main branch, `/docs`) |

## Adding an artifact

```bash
scripts/discover.sh          # find new sites / pages
# edit artifacts.json
scripts/thumbs.sh            # refresh thumbnails
python3 scripts/build.py     # rebuild docs/index.html
git commit -am "Add <artifact>" && git push
```
