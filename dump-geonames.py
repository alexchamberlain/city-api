import asyncio
import csv
import os

import attr

import asyncpg

COUNTRY_COLUMNS = [
    "ISO",
    "ISO3",
    "ISO-Numeric",
    "fips",
    "Country",
    "Capital",
    "Area(in sq km)",
    "Population",
    "Continent",
    "tld",
    "CurrencyCode",
    "CurrencyName",
    "Phone",
    "Postal Code Format",
    "Postal Code Regex",
    "Languages",
    "geonameid",
    "neighbours",
    "EquivalentFipsCode"
]

COLUMNS = [
    "geonameid",
    "name",
    "asciiname",
    "alternatenames",
    "latitude",
    "longitude",
    "feature class",
    "feature code",
    "country code",
    "cc2",
    "admin1 code",
    "admin2 code",
    "admin3 code",
    "admin4 code",
    "population",
    "elevation",
    "dem",
    "timezone",
    "modification date"
]

DSN = os.environ.get('DATABASE_URL')


@attr.s
class Country:
    iso = attr.ib()
    name = attr.ib()


@attr.s
class City:
    country_iso = attr.ib()
    geoname_id = attr.ib()
    name = attr.ib()
    latitude = attr.ib()
    longitude = attr.ib()
    population = attr.ib()


async def main():
    if DSN is None:
        print('export DATABASE_URL before running this script')
        return

    conn = await asyncpg.connect(DSN)

    async with conn.transaction():
        with open('countryInfo.txt', 'r') as f:
            rowreader = csv.DictReader(
                (row for row in f if not row.startswith('#')),
                fieldnames=COUNTRY_COLUMNS,
                delimiter='\t'
            )

            for row in rowreader:
                country = Country(iso=row['ISO'], name=row['Country'])
                await conn.execute(
                    '''
                        INSERT INTO country (iso, name)
                        VALUES ($1, $2)
                    ''',
                    country.iso,
                    country.name
                )

        with open('cities1000.txt', 'r') as f:
            rowreader = csv.DictReader(f, fieldnames=COLUMNS, delimiter='\t')

            for row in rowreader:
                city = City(
                    country_iso=row['country code'],
                    geoname_id=int(row['geonameid']),
                    name=row['name'],
                    latitude=float(row['latitude']),
                    longitude=float(row['longitude']),
                    population=int(row['population'])
                )

                await conn.execute(
                    '''
                        INSERT INTO city (country_iso, geoname_id, name, latitude, longitude, population)
                        VALUES ($1, $2, $3, $4, $5, $6)
                    ''',
                    city.country_iso,
                    city.geoname_id,
                    city.name,
                    city.latitude,
                    city.longitude,
                    city.population
                )

    await conn.close()

asyncio.get_event_loop().run_until_complete(main())
