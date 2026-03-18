DROP TABLE IF EXISTS task_service;

CREATE TABLE user (
    id TEXT PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    email VARCHAR(20) NOT NULL,
    password VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    updated_by_id TEXT NOT NULL,
    created_by_id TEXT NOT NULL,
    FOREIGN KEY (updated_by_id) REFERENCES user(id),
    FOREIGN KEY (created_by_id) REFERENCES user(id),
);

CREATE TABLE task_service (
    id TEXT PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    description VARCHAR(20) NOT NULL,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NULL,
    updated_by_id TEXT NOT NULL,
    created_by_id TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (updated_by_id) REFERENCES user(id),
    FOREIGN KEY (created_by_id) REFERENCES user(id),
);

