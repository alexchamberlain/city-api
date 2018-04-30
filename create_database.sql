CREATE TABLE IF NOT EXISTS country (
    iso char(2) PRIMARY KEY,
    name text
);

CREATE TABLE IF NOT EXISTS city (
    country_iso char(2),
    geoname_id int,
    name text,
    latitude numeric,
    longitude numeric,
    population int,
    FOREIGN KEY (country_iso) REFERENCES country (iso)
);

CREATE INDEX IF NOT EXISTS by_name ON city (name, population desc)
