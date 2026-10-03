#!/bin/bash
# Rebuild the wordmark and publish only when its content changes.
set -euo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
python3 tools/build.py >/dev/null

git add -- assets/header-dark.svg assets/header-light.svg README.md
git diff --cached --quiet && { echo "без изменений"; exit 0; }
git -c user.name=Xuisuki -c user.email=231307371+Xuisuki@users.noreply.github.com \
  commit -qm "refresh: profile artwork"
env -u HTTPS_PROXY -u HTTP_PROXY GIT_TERMINAL_PROMPT=0 \
  git -c credential.helper= -c credential.helper='!gh auth git-credential' \
  push -q origin main
echo "опубликовано: $(date -u +%F)"
