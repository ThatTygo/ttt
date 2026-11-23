#!/bin/bash
set -e
# Startrechten alleen bij de eerste start; daarna beheert een admin ze in de wiki.
mkdir -p /storage/conf
if [ ! -e /storage/conf/acl.auth.php ]; then
  cp /var/www/html/conf.core/acl.auth.ttt.php /storage/conf/acl.auth.php
fi
# Lege gebruikerslijst: DokuWiki's installatiewizard is dan niet nodig.
[ -e /storage/conf/users.auth.php ] || : > /storage/conf/users.auth.php
exec /dokuwiki-entrypoint.sh "$@"
