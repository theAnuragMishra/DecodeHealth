-- name: CreateRequest :exec
INSERT INTO requests (name, sequence, age, hospital_id, lab_id) VALUES ($1, $2, $3, $4, $5);

-- name: MarkRequestFulfilled :exec
UPDATE requests SET status = 'fulfilled' WHERE id = $1;

-- name: MarkRequestAccepted :exec
UPDATE requests SET status = 'accepted' WHERE id = $1;

-- name: MarkRequestDenied :exec
UPDATE requests SET status = 'denied' where id = $1;

-- name: DeleteRequest :exec
DELETE FROM requests WHERE id = $1;

-- name: GetRequestsForHospital :many
SELECT * FROM requests WHERE hospital_id = $1;

-- name: GetRequestsForLab :many
SELECT * FROM requests WHERE lab_id = $1;