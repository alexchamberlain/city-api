import itertools

from aiodataloader import DataLoader

from .models import Country, City


class CountryLoader(DataLoader):
    def __init__(self, db):
        super().__init__()
        self.db = db

    async def batch_load_fn(self, isos):
        query = 'SELECT iso, name FROM country WHERE iso = any($1::text[])'
        rows = await self.db.fetch(query, isos)
        mapping = {
            row['iso']: Country(
                iso=row['iso'],
                name=row['name']
            ) for row in rows
        }

        return [mapping.get(i) for i in isos]

    def resolver(self, context, resolve_info, *, iso):
        return self.load(iso)

    def context_resolver(self, context, resolve_info):
        return self.load(context.country_iso)


class CityLoader:
    def __init__(self, db):
        super().__init__()
        self.db = db

        self.geoname_id_loader = DataLoader(self.geoname_id_batch_load_fn)
        self.name_loader = DataLoader(self.name_batch_load_fn)
        self.country_iso_loader = DataLoader(self.country_iso_batch_load_fn)

    def geoname_id_load(self, key):
        return self.geoname_id_loader.load(key)

    async def geoname_id_batch_load_fn(self, keys):
        query = '''
            SELECT
                country_iso,
                geoname_id,
                name,
                latitude,
                longitude,
                population
            FROM city
            WHERE geoname_id = any($1::int[])
        '''
        rows = await self.db.fetch(query, keys)
        mapping = {
            row['geoname_id']: City(
                country_iso=row['country_iso'],
                geoname_id=row['geoname_id'],
                name=row['name'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                population=row['population']
            ) for row in rows
        }

        return [mapping.get(i) for i in keys]

    def name_load(self, key):
        return self.name_loader.load(key)

    async def name_batch_load_fn(self, keys):
        query = '''
            SELECT
                country_iso,
                geoname_id,
                name,
                latitude,
                longitude,
                population
            FROM city
            WHERE name = any($1::text[])
            ORDER BY name
        '''
        rows = await self.db.fetch(query, keys)

        mapping = {}
        for name, group in itertools.groupby(rows, key=lambda r: r['name']):
            mapping[name] = []
            row = next(group)
            city = City(
                country_iso=row['country_iso'],
                geoname_id=row['geoname_id'],
                name=row['name'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                population=row['population']
            )

            self.geoname_id_loader.prime(city.geoname_id, city)
            mapping[name] = city

        return [mapping.get(i) for i in keys]

    def country_iso_load(self, key):
        return self.country_iso_loader.load(key)

    async def country_iso_batch_load_fn(self, keys):
        query = '''
            SELECT
                country_iso,
                geoname_id,
                name,
                latitude,
                longitude,
                population
            FROM city
            WHERE country_iso = any($1::text[])
            ORDER BY country_iso, population DESC
        '''

        rows = await self.db.fetch(query, keys)

        mapping = {}

        for key, group in itertools.groupby(rows, key=lambda r: r['country_iso']):
            mapping[key] = []
            for row in group:
                city = City(
                    country_iso=row['country_iso'],
                    geoname_id=row['geoname_id'],
                    name=row['name'],
                    latitude=row['latitude'],
                    longitude=row['longitude'],
                    population=row['population']
                )

                self.geoname_id_loader.prime(city.geoname_id, city)
                mapping[key].append(city)

        return [mapping.get(i) for i in keys]
