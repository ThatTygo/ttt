<?php
declare(strict_types=1);

function admin_count(): int
{
    return (int) q("SELECT COUNT(*) FROM users WHERE role = 'admin' AND status = 'approved'")->fetchColumn();
}

// --- Eigen account -------------------------------------------------------

function account_update(): never
{
    $user = require_user();
    $b = json_body();
    $name = text_field($b, 'name', 'Naam', 2, 80, required: false);
    $newPassword = text_field($b, 'new_password', 'Nieuw wachtwoord', 10, 200, required: false, trim: false);
    if ($newPassword !== null) {
        $current = is_string($b['current_password'] ?? null) ? $b['current_password'] : '';
        if (!password_verify($current, $user['password_hash'])) {
            throw new ApiError(400, 'Je huidige wachtwoord klopt niet.');
        }
        q('UPDATE users SET password_hash = ? WHERE id = ?', [hash_password($newPassword), $user['id']]);
    }
    if ($name !== null) {
        q('UPDATE users SET name = ? WHERE id = ?', [$name, $user['id']]);
    }
    respond(200, user_out(row('SELECT * FROM users WHERE id = ?', [$user['id']])));
}

/** Inzagerecht (AVG art. 15): alles wat we over het account opslaan. */
function account_export(): never
{
    $user = require_user();
    $sessions = (int) q('SELECT COUNT(*) FROM sessions WHERE user_id = ? AND expires_at > ?', [$user['id'], now_utc()])->fetchColumn();
    respond(200, ['account' => user_out($user), 'actieve_sessies' => $sessions]);
}

function account_delete(): never
{
    $user = require_user();
    $password = json_body()['password'] ?? '';
    if (!is_string($password) || !password_verify($password, $user['password_hash'])) {
        throw new ApiError(400, 'Wachtwoord klopt niet.');
    }
    if ($user['role'] === 'admin' && admin_count() <= 1) {
        throw new ApiError(400, 'Je bent de laatste admin. Maak eerst iemand anders admin.');
    }
    end_session();
    q('DELETE FROM users WHERE id = ?', [$user['id']]);
    respond(204);
}

// --- Gebruikersbeheer (admin) -------------------------------------------

function users_list(): never
{
    require_role('admin');
    respond(200, array_map('user_out', rows('SELECT * FROM users ORDER BY status DESC, name')));
}

function users_update(array $p): never
{
    require_role('admin');
    $user = row('SELECT * FROM users WHERE id = ?', [(int) $p['id']]) ?? throw new ApiError(404, 'Gebruiker niet gevonden.');
    $b = json_body();
    $role = $b['role'] ?? null;
    $status = $b['status'] ?? null;
    if ($role !== null && !isset(ROLE_RANK[$role])) {
        throw new ApiError(422, 'Onbekende rol.');
    }
    if ($status !== null && !in_array($status, ['pending', 'approved'], true)) {
        throw new ApiError(422, 'Onbekende status.');
    }
    $losingAdmin = $user['role'] === 'admin' && $user['status'] === 'approved'
        && (($role !== null && $role !== 'admin') || $status === 'pending');
    if ($losingAdmin && admin_count() <= 1) {
        throw new ApiError(400, 'Er moet minstens één admin overblijven.');
    }
    if ($role !== null) {
        q('UPDATE users SET role = ? WHERE id = ?', [$role, $user['id']]);
    }
    if ($status !== null && $status !== $user['status']) {
        q('UPDATE users SET status = ?, approved_at = ? WHERE id = ?',
            [$status, $status === 'approved' ? now_utc() : null, $user['id']]);
        if ($status === 'pending') {
            q('DELETE FROM sessions WHERE user_id = ?', [$user['id']]);
        }
    }
    respond(200, user_out(row('SELECT * FROM users WHERE id = ?', [$user['id']])));
}

function users_delete(array $p): never
{
    $admin = require_role('admin');
    $user = row('SELECT * FROM users WHERE id = ?', [(int) $p['id']]) ?? throw new ApiError(404, 'Gebruiker niet gevonden.');
    if ((int) $user['id'] === (int) $admin['id']) {
        throw new ApiError(400, "Verwijder je eigen account via 'Mijn account'.");
    }
    if ($user['role'] === 'admin' && $user['status'] === 'approved' && admin_count() <= 1) {
        throw new ApiError(400, 'Er moet minstens één admin overblijven.');
    }
    q('DELETE FROM users WHERE id = ?', [$user['id']]);
    respond(204);
}
