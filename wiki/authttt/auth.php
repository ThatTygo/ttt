<?php

use dokuwiki\Extension\AuthPlugin;

/**
 * Inloggen via de TTT-site.
 *
 * Caddy vraagt bij elk verzoek aan de TTT-API wie er is ingelogd (forward_auth)
 * en zet het resultaat in X-Ttt-*-headers. Wie geen editor of admin is, komt
 * niet eens bij de wiki. Caddy verwijdert deze headers eerst uit het verzoek
 * van de bezoeker, dus ze zijn niet te vervalsen; de wiki-container is alleen
 * via Caddy bereikbaar.
 */
class auth_plugin_authttt extends AuthPlugin
{
    public function __construct()
    {
        parent::__construct();
        $this->cando['external'] = true;
        $this->cando['logout'] = false; // uitloggen gaat via de TTT-site
        $this->success = true;
    }

    public function trustExternal($user, $pass, $sticky = false)
    {
        global $USERINFO;

        $login = $_SERVER['HTTP_X_TTT_USER'] ?? '';
        if (!preg_match('/^ttt\d+$/', $login)) {
            return false;
        }
        $groups = array_values(array_intersect(
            explode(',', $_SERVER['HTTP_X_TTT_GROUPS'] ?? ''),
            ['user', 'editor', 'admin']
        ));

        $USERINFO = [
            'name' => rawurldecode($_SERVER['HTTP_X_TTT_NAME'] ?? $login),
            'mail' => $_SERVER['HTTP_X_TTT_EMAIL'] ?? '',
            'grps' => $groups,
        ];
        $_SERVER['REMOTE_USER'] = $login;
        $_SESSION[DOKU_COOKIE]['auth']['user'] = $login;
        $_SESSION[DOKU_COOKIE]['auth']['info'] = $USERINFO;
        $this->rememberName($login, $USERINFO['name']);
        return true;
    }

    public function getUserData($user, $requireGroups = true)
    {
        global $USERINFO;
        if (isset($_SERVER['REMOTE_USER']) && $user === $_SERVER['REMOTE_USER']) {
            return $USERINFO;
        }
        // Andere gebruikers: de naam van hun laatste bezoek, voor de bewerkingsgeschiedenis.
        $names = $this->names();
        if (!isset($names[$user])) {
            return false;
        }
        return ['name' => $names[$user], 'mail' => '', 'grps' => []];
    }

    /** Bestand met login => naam van iedereen die de wiki heeft bezocht. */
    private function namesFile(): string
    {
        global $conf;
        return $conf['metadir'] . '/_ttt_users.json';
    }

    private function names(): array
    {
        static $names = null;
        if ($names === null) {
            $raw = @file_get_contents($this->namesFile());
            $names = is_string($raw) ? (json_decode($raw, true) ?: []) : [];
        }
        return $names;
    }

    private function rememberName(string $login, string $name): void
    {
        $names = $this->names();
        if (($names[$login] ?? null) === $name) {
            return;
        }
        $names[$login] = $name;
        io_saveFile($this->namesFile(), json_encode($names, JSON_UNESCAPED_UNICODE));
    }
}
