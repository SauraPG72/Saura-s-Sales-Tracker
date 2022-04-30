DROP TABLE IF EXISTS clients;
DROP TABLE IF EXISTS users;



CREATE TABLE users(
    id SERIAL PRIMARY KEY, 
    email TEXT NOT NULL, 
    name TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE clients(
    client_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    client_name TEXT NOT NULL,
    company TEXT NOT NULL,
    phone INTEGER,
    email TEXT NOT NULL,
    suburb TEXT NOT NULL, 
    status INTEGER
);