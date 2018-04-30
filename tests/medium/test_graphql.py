import json
import os

import asyncpg
from graphql import graphql
from graphql.execution.executors.asyncio import AsyncioExecutor
import pytest

from cities import build_schema, CountryLoader, CityLoader

DSN = os.environ.get(
    'DATABASE_URL',
    'postgresql://achamberlai9@localhost/postgres'
)


@pytest.fixture
def queryer(event_loop):
    async def _(query):
        db = await asyncpg.connect(DSN, loop=event_loop)

        return await graphql(
            build_schema(),
            query,
            executor=AsyncioExecutor(loop=event_loop),
            context_value={
                'db': db,
                'loaders': {
                    'Country': CountryLoader(db),
                    'City': CityLoader(db)
                }
            },
            return_promise=True
        )

    return _


@pytest.mark.asyncio
async def test_country(queryer):
    result = await queryer('''
        query country {
          country(iso: "US") {
            iso
            name
            cities {
              geonameID
              name
            }
          }
        }
    ''')

    assert result.errors is None

    assert result.data['country']['iso'] == 'US'
    assert result.data['country']['name'] == 'United States'
    assert len(result.data['country']['cities']) == 16655

    assert result.data['country']['cities'][0] == {
        'geonameID': 5128581,
        'name': 'New York City'
    }


@pytest.mark.asyncio
async def test_city_by_id(queryer):
    result = await queryer('''
        query city_by_id {
          city(geonameID: 2643743) {
            geonameID
            name
            latitude
            longitude
            population
            country {
              iso
              name
            }
          }
        }
    ''')

    assert result.errors is None
    assert result.data == {
        "city": {
            "geonameID": 2643743,
            "name": "London",
            "latitude": 51.50853,
            "longitude": -0.12574,
            "population": 7556900,
            "country": {
                "iso": "GB",
                "name": "United Kingdom"
            }
        }
    }


@pytest.mark.asyncio
async def test_city_by_name(queryer):
    result = await queryer('''
        query city_by_name {
          city(name: "London") {
            geonameID
            name
            latitude
            longitude
            country {
              iso
              name
            }
          }
        }
    ''')

    assert result.errors is None
    assert result.data == {
        "city": {
            "geonameID": 2643743,
            "name": "London",
            "latitude": 51.50853,
            "longitude": -0.12574,
            "country": {
                "iso": "GB",
                "name": "United Kingdom"
            }
        }
    }


@pytest.mark.asyncio
async def test_city_by_id_multiple(queryer):
    result = await queryer('''
        query city_by_id {
          london: city(geonameID: 2643743) {
            geonameID
            name
            latitude
            longitude
            population
            country {
              iso
              name
            }
          }
          new_york: city(geonameID: 5128581) {
            geonameID
            name
            latitude
            longitude
            country {
              iso
              name
            }
          }
        }
    ''')

    data = _to_dict(result.data)
    print(data)

    assert result.errors is None
    assert data == {
        "london": {
            "geonameID": 2643743,
            "name": "London",
            "latitude": 51.50853,
            "longitude": -0.12574,
            "population": 7556900,
            "country": {
                "iso": "GB",
                "name": "United Kingdom"
            }
        },
        "new_york": {
            "geonameID": 5128581,
            "name": "New York City",
            "latitude": 40.71427,
            "longitude": -74.00597,
            "country": {
                "iso": "US",
                "name": "United States"
            }
        }
    }


def _to_dict(input_ordered_dict):
    return json.loads(json.dumps(input_ordered_dict))
