-- db_init/create_table.sql
CREATE TABLE IF NOT EXISTS people_info (
    h3index TEXT PRIMARY KEY,
    hexdistancetopark NUMERIC,
    married TEXT,
    municipality TEXT,
    postalcode TEXT,
    education TEXT,
    employment TEXT,
    numkids INTEGER,
    income INTEGER,
    age INTEGER,
    hoursWorked INTEGER,
    visitFrequency TEXT,
    wtp INTEGER
);
