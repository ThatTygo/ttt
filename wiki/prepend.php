<?php
// De wiki draait achter Caddy, die HTTPS afhandelt. De container is niet direct
// bereikbaar, dus X-Forwarded-Proto komt altijd van Caddy.
if (($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https') {
    $_SERVER['HTTPS'] = 'on';
}
