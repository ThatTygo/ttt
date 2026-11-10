<?php
declare(strict_types=1);

final class ApiError extends Exception
{
    public function __construct(public readonly int $status, string $message)
    {
        parent::__construct($message);
    }
}

function config(): array
{
    static $config = null;
    if ($config === null) {
        $file = __DIR__ . '/../config.php';
        if (!is_file($file)) {
            throw new ApiError(500, 'config.php ontbreekt. Kopieer config.sample.php naar config.php en vul hem in.');
        }
        $config = require $file;
    }
    return $config;
}

function db(): PDO
{
    static $pdo = null;
    if ($pdo === null) {
        $c = config()['db'];
        $dsn = sprintf('mysql:host=%s;port=%d;dbname=%s;charset=utf8mb4', $c['host'], $c['port'] ?? 3306, $c['name']);
        $pdo = new PDO($dsn, $c['user'], $c['password'], [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false,
        ]);
        $pdo->exec("SET time_zone = '+00:00'");
    }
    return $pdo;
}

function q(string $sql, array $params = []): PDOStatement
{
    $stmt = db()->prepare($sql);
    $stmt->execute($params);
    return $stmt;
}

function row(string $sql, array $params = []): ?array
{
    return q($sql, $params)->fetch() ?: null;
}

function rows(string $sql, array $params = []): array
{
    return q($sql, $params)->fetchAll();
}

// --- Tijd ----------------------------------------------------------------

function now_utc(int $offsetSeconds = 0): string
{
    return gmdate('Y-m-d H:i:s', time() + $offsetSeconds);
}

/** DATETIME (UTC) uit de database naar ISO 8601 voor de frontend. */
function iso(?string $value): ?string
{
    return $value === null ? null : str_replace(' ', 'T', $value) . 'Z';
}

/** Tijd uit een formulier naar UTC. Zonder tijdzone is het Amsterdamse tijd. */
function parse_datetime(mixed $value, string $label): ?string
{
    if ($value === null || $value === '') {
        return null;
    }
    if (!is_string($value)) {
        throw new ApiError(422, "$label is ongeldig.");
    }
    try {
        $dt = new DateTimeImmutable($value, new DateTimeZone(config()['timezone'] ?? 'Europe/Amsterdam'));
    } catch (Exception) {
        throw new ApiError(422, "$label is ongeldig.");
    }
    return $dt->setTimezone(new DateTimeZone('UTC'))->format('Y-m-d H:i:s');
}

// --- Request / response --------------------------------------------------

function json_body(): array
{
    static $body = null;
    if ($body === null) {
        $raw = file_get_contents('php://input') ?: '';
        $body = $raw === '' ? [] : json_decode($raw, true);
        if (!is_array($body)) {
            throw new ApiError(400, 'Ongeldige gegevens verstuurd.');
        }
    }
    return $body;
}

function respond(int $status, mixed $data = null): never
{
    http_response_code($status);
    header('Cache-Control: no-store');
    if ($status !== 204) {
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    }
    exit;
}

// --- Validatie -----------------------------------------------------------

function str_len(string $s): int
{
    return function_exists('mb_strlen') ? mb_strlen($s) : preg_match_all('/./us', $s);
}

function str_cut(string $s, int $length): string
{
    if (function_exists('mb_substr')) {
        return mb_substr($s, 0, $length);
    }
    return implode('', array_slice(preg_split('//u', $s, -1, PREG_SPLIT_NO_EMPTY), 0, $length));
}

/** Tekstveld: trimt, controleert lengte. Leeg + niet verplicht geeft null. */
function text_field(array $b, string $key, string $label, int $min, int $max, bool $required = true, bool $trim = true): ?string
{
    $value = $b[$key] ?? null;
    if (is_string($value) && $trim) {
        $value = trim($value);
    }
    if ($value === null || $value === '') {
        if ($required) {
            throw new ApiError(422, "$label is verplicht.");
        }
        return null;
    }
    if (!is_string($value)) {
        throw new ApiError(422, "$label is ongeldig.");
    }
    $len = str_len($value);
    if ($len < $min) {
        throw new ApiError(422, "$label is te kort (minimaal $min tekens).");
    }
    if ($len > $max) {
        throw new ApiError(422, "$label is te lang (maximaal $max tekens).");
    }
    return $value;
}

function email_field(array $b): string
{
    $email = is_string($b['email'] ?? null) ? strtolower(trim($b['email'])) : '';
    if ($email === '' || strlen($email) > 254 || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
        throw new ApiError(422, 'Vul een geldig e-mailadres in.');
    }
    return $email;
}

function int_field(array $b, string $key, string $label, int $min, int $max, bool $required = false): ?int
{
    $value = $b[$key] ?? null;
    if ($value === null || $value === '') {
        if ($required) {
            throw new ApiError(422, "$label is verplicht.");
        }
        return null;
    }
    if (!is_int($value) || $value < $min || $value > $max) {
        throw new ApiError(422, "$label is ongeldig.");
    }
    return $value;
}

function date_field(array $b, string $key, string $label): ?string
{
    $value = $b[$key] ?? null;
    if ($value === null || $value === '') {
        return null;
    }
    $dt = is_string($value) ? DateTimeImmutable::createFromFormat('!Y-m-d', $value) : false;
    if (!$dt || $dt->format('Y-m-d') !== $value) {
        throw new ApiError(422, "$label is geen geldige datum.");
    }
    return $value;
}

function bool_field(array $b, string $key, bool $default): bool
{
    $value = $b[$key] ?? $default;
    if (!is_bool($value)) {
        throw new ApiError(422, "$key is ongeldig.");
    }
    return $value;
}
