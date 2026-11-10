<?php
declare(strict_types=1);

// Eenmalige installatie: tabellen aanmaken, startinhoud laden en de eerste admin maken.
// Werkt alleen met de install_key uit config.php en zolang er nog geen admin is.
// Verwijder dit bestand van de server als de installatie klaar is.

require __DIR__ . '/src/bootstrap.php';
require __DIR__ . '/src/auth.php';

function install_tables(): void
{
    $sql = file_get_contents(__DIR__ . '/src/schema.sql');
    $sql = preg_replace('/^\s*--.*$/m', '', $sql);
    foreach (array_filter(array_map('trim', explode(';', $sql))) as $statement) {
        db()->exec($statement);
    }
}

function install_seed(): array
{
    $seed = json_decode(file_get_contents(__DIR__ . '/src/seed.json'), true);
    $done = [];
    $now = now_utc();
    if (!(int) q('SELECT COUNT(*) FROM members')->fetchColumn()) {
        foreach ($seed['members'] as $m) {
            q('INSERT INTO members (name, nickname, `function`, shift_day, member_since, active, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, 1, ?, ?)', [$m['name'], $m['nickname'], $m['function'], $m['shift_day'], $m['member_since'], $now, $now]);
        }
        $done[] = count($seed['members']) . ' leden toegevoegd';
    }
    if (!(int) q('SELECT COUNT(*) FROM column_posts')->fetchColumn()) {
        foreach ($seed['columns'] as $c) {
            q('INSERT INTO column_posts (title, body, author_name, published_at, updated_at) VALUES (?, ?, ?, ?, ?)',
                [$c['title'], $c['body'], $c['author_name'], $c['published_at'], $c['published_at']]);
        }
        $done[] = count($seed['columns']) . ' columns toegevoegd';
    }
    if (!row('SELECT id FROM counter WHERE id = 1')) {
        $c = $seed['counter'];
        q('INSERT INTO counter (id, last_incident_date, last_incident_text, sticker_count, updated_at) VALUES (1, ?, ?, ?, ?)',
            [$c['last_incident_date'], $c['last_incident_text'], $c['sticker_count'], $now]);
    }
    return $done;
}

function has_admin(): bool
{
    try {
        return (bool) q("SELECT COUNT(*) FROM users WHERE role = 'admin' AND status = 'approved'")->fetchColumn();
    } catch (PDOException) {
        return false; // tabellen bestaan nog niet
    }
}

$error = null;
$result = null;
try {
    $config = config();
    if (empty($config['install_key']) || empty($config['secret'])) {
        throw new ApiError(500, "Vul eerst 'secret' en 'install_key' in config.php in.");
    }
    db();
    $installed = has_admin();
    if (!$installed && ($_SERVER['REQUEST_METHOD'] ?? '') === 'POST') {
        if (!hash_equals((string) $config['install_key'], (string) ($_POST['install_key'] ?? ''))) {
            throw new ApiError(403, 'De installatiecode klopt niet.');
        }
        $b = $_POST;
        $name = text_field($b, 'name', 'Naam', 2, 80);
        $email = email_field($b);
        $password = text_field($b, 'password', 'Wachtwoord', 10, 200, trim: false);
        install_tables();
        $result = install_seed();
        q("INSERT INTO users (name, email, password_hash, role, status, created_at, approved_at) VALUES (?, ?, ?, 'admin', 'approved', ?, ?)",
            [$name, $email, hash_password($password), now_utc(), now_utc()]);
        $result[] = "admin-account voor $email aangemaakt";
        $installed = true;
    }
} catch (ApiError $e) {
    $error = $e->getMessage();
    $installed ??= false;
} catch (PDOException $e) {
    $error = 'Kan niet verbinden met de database. Controleer de gegevens in config.php. (' . $e->getMessage() . ')';
    $installed = false;
}

$h = fn (string $s) => htmlspecialchars($s, ENT_QUOTES, 'UTF-8');
?>
<!doctype html>
<html lang="nl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex">
  <title>Installatie · Trauma Tram Tellers</title>
  <style>
    body { font: 16px/1.5 system-ui, sans-serif; background: #f6f3ea; color: #10213a; margin: 0; padding: 40px 16px; }
    main { max-width: 460px; margin: 0 auto; background: #fff; border: 1px solid #e2dccd; border-radius: 14px; padding: 28px; }
    h1 { margin-top: 0; }
    label { display: block; font-weight: 600; font-size: 14px; margin-bottom: 14px; }
    input { display: block; width: 100%; box-sizing: border-box; margin-top: 4px; padding: 10px; border: 1.5px solid #e2dccd; border-radius: 8px; font: inherit; }
    button { background: #ffc72c; border: 0; border-radius: 999px; padding: 10px 20px; font: 600 16px system-ui; cursor: pointer; }
    .error { color: #d6452f; border: 1px solid #d6452f; padding: 10px 14px; border-radius: 8px; }
    .ok { color: #2f7d4f; border: 1px solid #2f7d4f; padding: 10px 14px; border-radius: 8px; }
  </style>
</head>
<body>
<main>
  <h1>Installatie</h1>
  <?php if ($error): ?><p class="error"><?= $h($error) ?></p><?php endif ?>

  <?php if ($result): ?>
    <p class="ok">Klaar: <?= $h(implode(', ', $result)) ?>.</p>
    <p><strong>Verwijder nu <code>api/install.php</code> van de server.</strong> Daarna kun je <a href="/inloggen">inloggen</a>.</p>
  <?php elseif ($installed): ?>
    <p>De site is al geïnstalleerd. Verwijder <code>api/install.php</code> van de server.</p>
  <?php else: ?>
    <p>Hiermee maak je de tabellen aan, worden de columns en leden ingeladen en maak je het eerste admin-account.</p>
    <form method="post">
      <label>Installatiecode (install_key uit config.php)<input name="install_key" type="password" required></label>
      <label>Jouw naam<input name="name" required minlength="2" maxlength="80"></label>
      <label>E-mailadres<input name="email" type="email" required></label>
      <label>Wachtwoord (min. 10 tekens)<input name="password" type="password" minlength="10" required></label>
      <button>Installeren</button>
    </form>
  <?php endif ?>
</main>
</body>
</html>
