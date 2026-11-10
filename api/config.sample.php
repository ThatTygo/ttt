<?php
// Kopieer dit bestand naar config.php (op de server, in de map api/) en vul het in.
// config.php staat niet in git en wordt niet meegenomen door build.sh,
// dus bij een update wordt hij niet overschreven.

return [
    // De MySQL-gegevens uit het Strato-panel (Database → Beheer).
    'db' => [
        'host' => 'database-XXXXXXXX.webspace-host.com',
        'port' => 3306,
        'name' => 'dbsXXXXXXXX',
        'user' => 'dbuXXXXXXXX',
        'password' => '',
    ],

    // Lange willekeurige tekst. Wordt gebruikt om IP-adressen te hashen.
    // Maak er een met: php -r 'echo bin2hex(random_bytes(32));'
    'secret' => '',

    // Geheime code die je nodig hebt om install.php te gebruiken.
    'install_key' => '',

    'timezone' => 'Europe/Amsterdam',
    'session_days' => 30,

    // null = automatisch (Secure-cookie zodra de site via HTTPS draait).
    'cookie_secure' => null,
];
