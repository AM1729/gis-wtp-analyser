-- db_init/create_table.sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS survey_info (
    response_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    h3index TEXT,
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
