-- +goose Up
CREATE TABLE orgs(
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    role VARCHAR(15) NOT NULL CHECK(role IN ('hospital', 'lab')),
    password_hash TEXT NOT NULL
);

-- +goose Down
DROP TABLE orgs;