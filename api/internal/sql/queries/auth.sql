-- name: CreateSession :exec
INSERT INTO sessions(id, org_id, expires_at)
VALUES ($1, $2, $3);

-- name: GetSession :one
SELECT * FROM sessions WHERE id = $1;

-- name: UpdateSessionExpiry :exec
UPDATE sessions SET expires_at = $1 WHERE id = $2;

-- name: DeleteSession :exec
DELETE FROM sessions WHERE id = $1;