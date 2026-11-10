<?php
declare(strict_types=1);

function column_out(array $c): array
{
    return [
        'id' => (int) $c['id'],
        'title' => $c['title'],
        'body' => $c['body'],
        'author_name' => $c['author_name'],
        'published_at' => iso($c['published_at']),
        'updated_at' => iso($c['updated_at']),
    ];
}

function excerpt(string $body, int $length = 220): string
{
    $text = trim(preg_replace('/\s+/u', ' ', $body));
    if (str_len($text) <= $length) {
        return $text;
    }
    $cut = str_cut($text, $length);
    $space = strrpos($cut, ' ');
    return ($space !== false ? substr($cut, 0, $space) : $cut) . '…';
}

function query_int(string $key, int $default, int $min, int $max): int
{
    $value = filter_var($_GET[$key] ?? $default, FILTER_VALIDATE_INT);
    return $value === false ? $default : max($min, min($max, $value));
}

function columns_list(): never
{
    $where = [];
    $params = [];
    $search = is_string($_GET['q'] ?? null) ? trim(str_cut($_GET['q'], 100)) : '';
    if ($search !== '') {
        $like = '%' . addcslashes($search, '\\%_') . '%';
        $where[] = '(title LIKE ? OR body LIKE ?)';
        array_push($params, $like, $like);
    }
    $author = is_string($_GET['author'] ?? null) ? $_GET['author'] : '';
    if ($author !== '') {
        $where[] = 'author_name = ?';
        $params[] = $author;
    }
    $sqlWhere = $where ? 'WHERE ' . implode(' AND ', $where) : '';
    $limit = query_int('limit', 12, 1, 100);
    $offset = query_int('offset', 0, 0, PHP_INT_MAX);

    $total = (int) q("SELECT COUNT(*) FROM column_posts $sqlWhere", $params)->fetchColumn();
    $items = rows("SELECT id, title, author_name, published_at, body FROM column_posts $sqlWhere
                   ORDER BY published_at DESC LIMIT $limit OFFSET $offset", $params);
    $authors = q('SELECT DISTINCT author_name FROM column_posts ORDER BY author_name')->fetchAll(PDO::FETCH_COLUMN);

    respond(200, [
        'items' => array_map(fn ($c) => [
            'id' => (int) $c['id'],
            'title' => $c['title'],
            'author_name' => $c['author_name'],
            'published_at' => iso($c['published_at']),
            'excerpt' => excerpt($c['body']),
        ], $items),
        'total' => $total,
        'authors' => $authors,
    ]);
}

function find_column(array $p): array
{
    return row('SELECT * FROM column_posts WHERE id = ?', [(int) $p['id']]) ?? throw new ApiError(404, 'Column niet gevonden.');
}

function column_input(): array
{
    $b = json_body();
    return [
        'title' => text_field($b, 'title', 'Titel', 1, 160),
        'body' => text_field($b, 'body', 'Tekst', 1, 20000, trim: false),
        'author_name' => text_field($b, 'author_name', 'Auteur', 1, 120),
        'published_at' => parse_datetime($b['published_at'] ?? null, 'Datum'),
    ];
}

function columns_get(array $p): never
{
    respond(200, column_out(find_column($p)));
}

function columns_create(): never
{
    $user = require_role('editor');
    $c = column_input();
    q('INSERT INTO column_posts (title, body, author_name, published_at, created_by_id, updated_by_id, updated_at)
       VALUES (?, ?, ?, ?, ?, ?, ?)',
        [$c['title'], $c['body'], $c['author_name'], $c['published_at'] ?? now_utc(), $user['id'], $user['id'], now_utc()]);
    respond(201, column_out(find_column(['id' => db()->lastInsertId()])));
}

function columns_update(array $p): never
{
    $user = require_role('editor');
    $column = find_column($p);
    $c = column_input();
    q('UPDATE column_posts SET title = ?, body = ?, author_name = ?, published_at = ?, updated_by_id = ?, updated_at = ? WHERE id = ?',
        [$c['title'], $c['body'], $c['author_name'], $c['published_at'] ?? $column['published_at'], $user['id'], now_utc(), $column['id']]);
    respond(200, column_out(find_column($p)));
}

function columns_delete(array $p): never
{
    require_role('editor');
    $column = find_column($p);
    q('DELETE FROM column_posts WHERE id = ?', [$column['id']]);
    respond(204);
}

// --- Teller --------------------------------------------------------------

function counter_out(): array
{
    $c = row('SELECT * FROM counter WHERE id = 1');
    if ($c === null) {
        q('INSERT INTO counter (id, sticker_count, updated_at) VALUES (1, 0, ?)', [now_utc()]);
        $c = row('SELECT * FROM counter WHERE id = 1');
    }
    return [
        'last_incident_date' => $c['last_incident_date'],
        'last_incident_text' => $c['last_incident_text'],
        'sticker_count' => (int) $c['sticker_count'],
        'updated_at' => iso($c['updated_at']),
    ];
}

function counter_get(): never
{
    respond(200, counter_out());
}

function counter_update(): never
{
    require_role('editor');
    counter_out(); // zorgt dat de rij bestaat
    $b = json_body();
    q('UPDATE counter SET last_incident_date = ?, last_incident_text = ?, sticker_count = ?, updated_at = ? WHERE id = 1', [
        date_field($b, 'last_incident_date', 'Datum laatste incident'),
        text_field($b, 'last_incident_text', 'Omschrijving', 0, 300, required: false),
        int_field($b, 'sticker_count', 'Aantal stickers', 0, 100000, required: true),
        now_utc(),
    ]);
    respond(200, counter_out());
}
