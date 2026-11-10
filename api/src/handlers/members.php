<?php
declare(strict_types=1);

// De ledenadministratie is in zijn geheel alleen voor admins (AVG).
// Editors zien via het rooster alleen naam + dienstdag.

function member_out(array $m): array
{
    return [
        'id' => (int) $m['id'],
        'name' => $m['name'],
        'nickname' => $m['nickname'],
        'function' => $m['function'],
        'shift_day' => $m['shift_day'] === null ? null : (int) $m['shift_day'],
        'member_since' => $m['member_since'],
        'active' => (bool) $m['active'],
        'notes' => $m['notes'],
        'user_id' => $m['user_id'] === null ? null : (int) $m['user_id'],
    ];
}

function member_input(): array
{
    $b = json_body();
    $userId = int_field($b, 'user_id', 'Gekoppeld account', 1, PHP_INT_MAX);
    if ($userId !== null && !row('SELECT id FROM users WHERE id = ?', [$userId])) {
        throw new ApiError(400, 'Gekoppeld account bestaat niet.');
    }
    return [
        'name' => text_field($b, 'name', 'Naam', 1, 80),
        'nickname' => text_field($b, 'nickname', 'Bijnaam', 0, 80, required: false),
        'function' => text_field($b, 'function', 'Functie', 0, 80, required: false),
        'shift_day' => int_field($b, 'shift_day', 'Dagdienst', 0, 6),
        'member_since' => date_field($b, 'member_since', 'Lid sinds'),
        'active' => bool_field($b, 'active', true) ? 1 : 0,
        'notes' => text_field($b, 'notes', 'Notities', 0, 2000, required: false),
        'user_id' => $userId,
    ];
}

function find_member(array $p): array
{
    return row('SELECT * FROM members WHERE id = ?', [(int) $p['id']]) ?? throw new ApiError(404, 'Lid niet gevonden.');
}

function members_list(): never
{
    require_role('admin');
    respond(200, array_map('member_out', rows('SELECT * FROM members ORDER BY active DESC, name')));
}

function members_create(): never
{
    require_role('admin');
    $m = member_input();
    q('INSERT INTO members (name, nickname, `function`, shift_day, member_since, active, notes, user_id, created_at, updated_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', [...array_values($m), now_utc(), now_utc()]);
    respond(201, member_out(row('SELECT * FROM members WHERE id = ?', [db()->lastInsertId()])));
}

function members_update(array $p): never
{
    require_role('admin');
    $member = find_member($p);
    $m = member_input();
    q('UPDATE members SET name = ?, nickname = ?, `function` = ?, shift_day = ?, member_since = ?, active = ?, notes = ?,
       user_id = ?, updated_at = ? WHERE id = ?', [...array_values($m), now_utc(), $member['id']]);
    respond(200, member_out(find_member($p)));
}

function members_delete(array $p): never
{
    require_role('admin');
    $member = find_member($p);
    q('DELETE FROM members WHERE id = ?', [$member['id']]);
    respond(204);
}

function roster_get(): never
{
    require_role('editor');
    $members = rows('SELECT name, shift_day FROM members WHERE active = 1 AND shift_day IS NOT NULL ORDER BY name');
    $days = [];
    for ($day = 0; $day < 7; $day++) {
        $names = array_column(array_filter($members, fn ($m) => (int) $m['shift_day'] === $day), 'name');
        $days[] = ['day' => $day, 'names' => array_values($names)];
    }
    respond(200, $days);
}
