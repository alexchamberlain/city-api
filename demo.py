import json
import os

import asyncpg
from graphql import graphql
from graphql.execution.executors.asyncio import AsyncioExecutor

from cities import build_schema, CountryLoader, CityLoader

DSN = os.environ.get('DATABASE_URL')


async def main(loop):
    if DSN is None:
        print('export DATABASE_URL before running this script')
        return

    db = await asyncpg.connect(DSN, loop=loop)

    query = '''
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
    '''

    result = await graphql(
        build_schema(),
        query,
        executor=AsyncioExecutor(loop=loop),
        context_value={
            'db': db,
            'loaders': {
                'Country': CountryLoader(db),
                'City': CityLoader(db)
            }
        },
        return_promise=True
    )

    assert result.errors is None

    print(json.dumps(result.data, sort_keys=True, indent=4))


import asyncio

loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))
loop.close()
