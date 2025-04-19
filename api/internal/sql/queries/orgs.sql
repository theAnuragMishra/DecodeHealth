-- name: CreateOrg :exec
INSERT INTO orgs (name, kind, password_hash) VALUES ($1, $2, $3);

-- name: GetOrg :one
SELECT * FROM orgs WHERE id = $1;

-- name: GetLabs :many
SELECT * FROM orgs WHERE role = 'lab';