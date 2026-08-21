#!/bin/bash
# Пересобирает карточку активности и публикует её.
#
# Собирается на сервере, а не в GitHub Actions: токен рабочего процесса Actions
# не видит вклады в приватные репозитории даже при включённом их показе в профиле
# (проверено — он отдавал 13 вкладов вместо 478). Личный токен остаётся здесь и
# в настройки репозитория не попадает.
set -euo pipefail

cd /srv/tools/Xuisuki
export GITHUB_TOKEN=$(cat /root/.config/github/xuisuki_pat)
export XTOK="$GITHUB_TOKEN"

env -u HTTPS_PROXY -u HTTP_PROXY python3 tools/build.py >/dev/null

# адрес картинки меняется вместе с датой, иначе читателю отдаётся вчерашняя из кэша
stamp=$(date -u +%Y%m%d)
sed -i -E "s/\.svg\?v=[0-9]+/.svg?v=$stamp/g" README.md

git add assets README.md
git diff --cached --quiet && { echo "без изменений"; exit 0; }
# подпись задаётся явно: под systemd домашнего каталога нет и ~/.gitconfig не читается
git -c user.name=Xuisuki -c user.email=231307371+Xuisuki@users.noreply.github.com \
   commit -qm "refresh: activity $(date -u +%F)"
env -u HTTPS_PROXY -u HTTP_PROXY GIT_TERMINAL_PROMPT=0 \
  git -c credential.helper= \
      -c credential.helper='!f(){ echo username=x-access-token; echo "password=$XTOK"; };f' \
  push -q origin main
echo "опубликовано: $(date -u +%F)"
