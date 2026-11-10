<?php
declare(strict_types=1);

// Alle /api/*-verzoeken komen hier binnen (zie .htaccess in de webroot).

require __DIR__ . '/src/bootstrap.php';
require __DIR__ . '/src/auth.php';
foreach (glob(__DIR__ . '/src/handlers/*.php') as $file) {
    require $file;
}

const ROUTES = [
    ['POST', '/auth/register', 'auth_register'],
    ['POST', '/auth/login', 'auth_login'],
    ['POST', '/auth/logout', 'auth_logout'],
    ['GET', '/auth/me', 'auth_me'],

    ['PATCH', '/account', 'account_update'],
    ['GET', '/account/export', 'account_export'],
    ['DELETE', '/account', 'account_delete'],

    ['GET', '/users', 'users_list'],
    ['PATCH', '/users/{id}', 'users_update'],
    ['DELETE', '/users/{id}', 'users_delete'],

    ['GET', '/members', 'members_list'],
    ['POST', '/members', 'members_create'],
    ['PUT', '/members/{id}', 'members_update'],
    ['DELETE', '/members/{id}', 'members_delete'],
    ['GET', '/roster', 'roster_get'],

    ['GET', '/columns', 'columns_list'],
    ['GET', '/columns/{id}', 'columns_get'],
    ['POST', '/columns', 'columns_create'],
    ['PUT', '/columns/{id}', 'columns_update'],
    ['DELETE', '/columns/{id}', 'columns_delete'],

    ['GET', '/counter', 'counter_get'],
    ['PUT', '/counter', 'counter_update'],

    ['GET', '/health', 'health'],
];

function health(): never
{
    respond(200, ['ok' => true]);
}

function dispatch(string $method, string $path): never
{
    $pathMatched = false;
    foreach (ROUTES as [$routeMethod, $pattern, $handler]) {
        $regex = '#^' . preg_replace('#\{(\w+)\}#', '(?P<$1>\d+)', $pattern) . '$#';
        if (!preg_match($regex, $path, $params)) {
            continue;
        }
        $pathMatched = true;
        if ($routeMethod === $method) {
            $handler(array_filter($params, 'is_string', ARRAY_FILTER_USE_KEY));
        }
    }
    throw new ApiError($pathMatched ? 405 : 404, $pathMatched ? 'Methode niet toegestaan.' : 'Niet gevonden.');
}

try {
    $method = $_SERVER['REQUEST_METHOD'] ?? 'GET';
    // Extra bescherming tegen CSRF: schrijfacties moeten JSON sturen
    // (een formulier van een andere site kan dat niet).
    if (!in_array($method, ['GET', 'HEAD', 'OPTIONS'], true)) {
        $type = $_SERVER['CONTENT_TYPE'] ?? '';
        $hasBody = (int) ($_SERVER['CONTENT_LENGTH'] ?? 0) > 0;
        if ($hasBody && !str_starts_with(strtolower($type), 'application/json')) {
            throw new ApiError(415, 'Verstuur gegevens als JSON.');
        }
    }
    $uri = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH) ?: '/';
    $pos = strpos($uri, '/api/');
    $path = rtrim($pos === false ? '/' : substr($uri, $pos + 4), '/') ?: '/';
    dispatch($method, $path);
} catch (ApiError $e) {
    respond($e->status, ['detail' => $e->getMessage()]);
} catch (Throwable $e) {
    error_log('[ttt] ' . $e);
    respond(500, ['detail' => 'Er ging iets mis op de server.']);
}
