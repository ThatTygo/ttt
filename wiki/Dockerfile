FROM dokuwiki/dokuwiki:stable

# Inloggen via de TTT-accounts. Plugins in plugins.core worden bij elke start in
# de opslag gelinkt, dus een update van deze plugin komt mee met een nieuw image.
COPY authttt /var/www/html/lib/plugins.core/authttt

# Vaste instellingen en startrechten.
COPY ttt.protected.php /var/www/html/conf.core/ttt.protected.php
COPY acl.auth.php /var/www/html/conf.core/acl.auth.ttt.php
RUN printf "\narray_push(\$config_cascade['main']['protected'], '/var/www/html/conf.core/ttt.protected.php');\n" \
      >> /var/www/html/inc/preload.php

# HTTPS achter Caddy herkennen (zie prepend.php).
COPY prepend.php /tmp/ttt-prepend.php
RUN tail -n +2 /tmp/ttt-prepend.php >> /var/www/html/.autoprepend.php && rm /tmp/ttt-prepend.php

COPY --chmod=755 entrypoint.sh /ttt-entrypoint.sh
ENTRYPOINT ["/ttt-entrypoint.sh"]
