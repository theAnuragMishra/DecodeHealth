-- +goose Up

CREATE TABLE sessions(
                         id TEXT PRIMARY KEY,
                         org_id INTEGER NOT NULL,
                         expires_at TIMESTAMP NOT NULL,
                         FOREIGN KEY (org_id) REFERENCES orgs(id) ON DELETE CASCADE
);


-- +goose Down

DROP TABLE sessions;