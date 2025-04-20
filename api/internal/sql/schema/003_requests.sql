-- +goose Up
CREATE TABLE requests (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    sequence TEXT NOT NULL,
    age SMALLINT NOT NULL,
    hospital_id INT NOT NULL REFERENCES orgs(id),
    lab_id INT NOT NULL REFERENCES orgs(id),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK(status in ('pending', 'accepted', 'fulfilled', 'denied')),
    report TEXT
);

-- +goose Down
DROP TABLE requests;