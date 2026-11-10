<?php
declare(strict_types=1);

const ROLE_RANK = ['user' => 0, 'editor' => 1, 'admin' => 2];
const SESSION_COOKIE = 'ttt_session';

function hash_password(string $password): string
{
    // Argon2id als de server het ondersteunt, anders bcrypt.
    return password_hash($password, defined('PASSWORD_ARGON2ID') ? PASSWORD_ARGON2ID : PASSWORD_DEFAULT);
}

function is_https(): bool
{
    return in_array(strtolower((string) ($_SERVER['HTTPS'] ?? '')), ['on', '1'], true)
        || ($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https'
        || (string) ($_SERVER['SERVER_PORT'] ?? '') === '443';
}

function cookie_secure(): bool
{
    return config()['cookie_secure'] ?? is_https();
}

function session_days(): int
{
    return (int) (config()['session_days'] ?? 30);
}

function start_session(array $user): void
{
    $token = rtrim(strtr(base64_encode(random_bytes(32)), '+/', '-_'), '=');
    $seconds = session_days() * 86400;
    q('DELETE FROM sessions WHERE expires_at < ?', [now_utc()]);
    q('INSERT INTO sessions (token_hash, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)',
        [hash('sha256', $token), $user['id'], now_utc(), now_utc($seconds)]);
    q('UPDATE users SET last_login_at = ? WHERE id = ?', [now_utc(), $user['id']]);
    setcookie(SESSION_COOKIE, $token, [
        'expires' => time() + $seconds,
        'path' => '/',
        'secure' => cookie_secure(),
        'httponly' => true,
        'samesite' => 'Lax',
    ]);
}

function end_session(): void
{
    $token = $_COOKIE[SESSION_COOKIE] ?? null;
    if (is_string($token)) {
        q('DELETE FROM sessions WHERE token_hash = ?', [hash('sha256', $token)]);
    }
    setcookie(SESSION_COOKIE, '', ['expires' => 1, 'path' => '/', 'secure' => cookie_secure(), 'httponly' => true, 'samesite' => 'Lax']);
}

/** Ingelogde, goedgekeurde gebruiker of null. */
function current_user(): ?array
{
    static $loaded = false, $user = null;
    if (!$loaded) {
        $loaded = true;
        $token = $_COOKIE[SESSION_COOKIE] ?? null;
        if (is_string($token) && $token !== '') {
            $user = row(
                "SELECT u.* FROM sessions s JOIN users u ON u.id = s.user_id
                 WHERE s.token_hash = ? AND s.expires_at > ? AND u.status = 'approved'",
                [hash('sha256', $token), now_utc()],
            );
        }
    }
    return $user;
}

function require_user(): array
{
    return current_user() ?? throw new ApiError(401, 'Je bent niet ingelogd.');
}

function require_role(string $role): array
{
    $user = require_user();
    if (ROLE_RANK[$user['role']] < ROLE_RANK[$role]) {
        throw new ApiError(403, 'Daar heb je de rechten niet voor.');
    }
    return $user;
}

function user_out(array $u): array
{
    return [
        'id' => (int) $u['id'],
        'name' => $u['name'],
        'email' => $u['email'],
        'role' => $u['role'],
        'status' => $u['status'],
        'created_at' => iso($u['created_at']),
        'last_login_at' => iso($u['last_login_at']),
    ];
}

/**
 * Simpele limiet per IP tegen brute-force. Het IP-adres wordt alleen gehasht
 * opgeslagen en na een uur gewist (zie privacybeleid).
 */
function rate_limit(string $bucket, int $maxHits, int $windowSeconds): void
{
    $ipHash = hash_hmac('sha256', (string) ($_SERVER['REMOTE_ADDR'] ?? '?'), config()['secret']);
    q('DELETE FROM rate_limits WHERE created_at < ?', [now_utc(-3600)]);
    $hits = (int) q('SELECT COUNT(*) FROM rate_limits WHERE bucket = ? AND ip_hash = ? AND created_at > ?',
        [$bucket, $ipHash, now_utc(-$windowSeconds)])->fetchColumn();
    if ($hits >= $maxHits) {
        throw new ApiError(429, 'Te veel pogingen. Probeer het over een paar minuten opnieuw.');
    }
    q('INSERT INTO rate_limits (bucket, ip_hash, created_at) VALUES (?, ?, ?)', [$bucket, $ipHash, now_utc()]);
}
