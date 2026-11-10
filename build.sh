#!/usr/bin/env bash
# Bouwt de map deploy/ die je in z'n geheel naar de webruimte van Strato uploadt.
set -euo pipefail
cd "$(dirname "$0")"

(cd frontend && npm ci && npm run build)

rm -rf deploy
mkdir deploy
cp -r frontend/dist/. deploy/
cp -r api deploy/api
# config.php staat alleen op de server en wordt dus nooit overschreven.
rm -f deploy/api/config.php

echo "Klaar: upload de inhoud van deploy/ naar de webroot van je domein."
