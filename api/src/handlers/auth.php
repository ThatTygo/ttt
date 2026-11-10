<?php
declare(strict_types=1);

function find_user_by_email(string $email): ?array
{
    return row('SELECT * FROM users WHERE email = ?', [strtolower($email)]);
}

function auth_register(): never
{
    rate_limit('register', 5, 3600);
    $b = json_body();
    $name = text_field($b, 'name', 'Naam', 2, 80);
    $email = email_field($b);
    $password = text_field($b, 'password', 'Wachtwoord', 10, 200, trim: false);
    if (find_user_by_email($email)) {
        throw new ApiError(409, 'Er bestaat al een account met dit e-mailadres.');
    }
    q("INSERT INTO users (name, email, password_hash, role, status, created_at) VALUES (?, ?, ?, 'user', 'pending', ?)",
        [$name, $email, hash_password($password), now_utc()]);
    respond(201, ['message' => 'Account aangemaakt. Een admin moet je account nog goedkeuren voordat je kunt inloggen.']);
}

function auth_login(): never
{
    rate_limit('login', 10, 300);
    $b = json_body();
    $email = is_string($b['email'] ?? null) ? trim($b['email']) : '';
    $password = is_string($b['password'] ?? null) ? $b['password'] : '';
    $user = $email !== '' ? find_user_by_email($email) : null;
    if ($user === null) {
        // Even lang rekenen als bij een bestaand account, zodat je niet kunt raden welke e-mails bestaan.
        hash_password($password); // kost evenveel tijd als een echte controle
        throw new ApiError(401, 'E-mailadres of wachtwoord klopt niet.');
    }
    if (!password_verify($password, $user['password_hash'])) {
        throw new ApiError(401, 'E-mailadres of wachtwoord klopt niet.');
    }
    if ($user['status'] !== 'approved') {
        throw new ApiError(403, 'Je account wacht nog op goedkeuring door een admin.');
    }
    if (password_needs_rehash($user['password_hash'], defined('PASSWORD_ARGON2ID') ? PASSWORD_ARGON2ID : PASSWORD_DEFAULT)) {
        q('UPDATE users SET password_hash = ? WHERE id = ?', [hash_password($password), $user['id']]);
    }
    start_session($user);
    respond(200, user_out(row('SELECT * FROM users WHERE id = ?', [$user['id']])));
}

function auth_logout(): never
{
    end_session();
    respond(204);
}

function auth_me(): never
{
    respond(200, user_out(require_user()));
}
