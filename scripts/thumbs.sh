#!/usr/bin/env bash
# Re-capture thumbnails for every page in artifacts.json (macOS, Google Chrome).
set -euo pipefail
cd "$(dirname "$0")/../docs/thumbs"
C="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
python3 -I - "$(dirname "$PWD")/../artifacts.json" <<'PY' | while read -r url name; do
import json,sys
m=json.load(open(sys.argv[1]))
for c in m["collections"]:
    for p in c["pages"]:
        path=p["path"]; s=path.rstrip("/")
        n=c["repo"]+("__"+s.replace(".html","").replace("/","__") if s else "")
        if not s or path.endswith("/"): n+="__index"
        print(f"https://{m['owner']}.github.io/{c['repo']}/{path} {n}")
PY
  echo "$name"
  "$C" --headless=new --disable-gpu --hide-scrollbars --window-size=1440,900 \
    --virtual-time-budget=6000 --screenshot="$PWD/$name.png" "$url" >/dev/null 2>&1
  sips -Z 720 "$name.png" --out "$name.png" >/dev/null
  sips -s format jpeg -s formatOptions 72 "$name.png" --out "$name.jpg" >/dev/null && rm "$name.png"
done
