# City API: GraphQL Example Server

Example server written for "GraphQL in Python" talk at PyLondinium 2018.

## Setup

Acquire cities1000.txt and countriesInfo.txt from [Geonames][1]. You'll need
a clean Postgres database. You can use
[`create_database.sql`](create_database.sql) to setup the tables, then export
DATABASE_URL before running [`dump-geonames.py`](dump-geonames.py) to load
the database with sample data.

## Attribution

The data used for this example comes from [Geonames][1] under a Creative Commons
Attribution 3.0 License. Although not modified, only a subset of the data is
used.

## License

Released under MIT License, Copyright (c) 2018 Alex Chamberlain. See
[`LICENSE.md`](LICENSE.md) for full details.

[1]: http://www.geonames.org/export/
