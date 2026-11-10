-- Alle tijden worden in UTC opgeslagen.

CREATE TABLE IF NOT EXISTS users (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(80) NOT NULL,
  email VARCHAR(254) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(16) NOT NULL DEFAULT 'user',
  status VARCHAR(16) NOT NULL DEFAULT 'pending',
  created_at DATETIME NOT NULL,
  approved_at DATETIME NULL,
  last_login_at DATETIME NULL,
  UNIQUE KEY uq_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- SHA-256 van het sessietoken; het token zelf staat alleen in de cookie.
CREATE TABLE IF NOT EXISTS sessions (
  token_hash CHAR(64) NOT NULL PRIMARY KEY,
  user_id INT UNSIGNED NOT NULL,
  created_at DATETIME NOT NULL,
  expires_at DATETIME NOT NULL,
  KEY ix_sessions_user (user_id),
  CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS members (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(80) NOT NULL,
  nickname VARCHAR(80) NULL,
  `function` VARCHAR(80) NULL,
  -- 0 = maandag ... 6 = zondag; dag waarop dit lid de column schrijft.
  shift_day TINYINT NULL,
  member_since DATE NULL,
  active TINYINT(1) NOT NULL DEFAULT 1,
  notes TEXT NULL,
  user_id INT UNSIGNED NULL,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  CONSTRAINT fk_members_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS column_posts (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(160) NOT NULL,
  body MEDIUMTEXT NOT NULL,
  author_name VARCHAR(120) NOT NULL,
  published_at DATETIME NOT NULL,
  created_by_id INT UNSIGNED NULL,
  updated_by_id INT UNSIGNED NULL,
  updated_at DATETIME NOT NULL,
  KEY ix_column_posts_published (published_at),
  CONSTRAINT fk_columns_created FOREIGN KEY (created_by_id) REFERENCES users (id) ON DELETE SET NULL,
  CONSTRAINT fk_columns_updated FOREIGN KEY (updated_by_id) REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Eén rij met de stand van de teller op de homepage.
CREATE TABLE IF NOT EXISTS counter (
  id TINYINT UNSIGNED NOT NULL PRIMARY KEY,
  last_incident_date DATE NULL,
  last_incident_text VARCHAR(300) NULL,
  sticker_count INT UNSIGNED NOT NULL DEFAULT 0,
  updated_at DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Pogingen per (gehasht) IP-adres voor inloggen/aanmelden; wordt na 1 uur gewist.
CREATE TABLE IF NOT EXISTS rate_limits (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  bucket VARCHAR(32) NOT NULL,
  ip_hash CHAR(64) NOT NULL,
  created_at DATETIME NOT NULL,
  KEY ix_rate_limits_lookup (bucket, ip_hash, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
