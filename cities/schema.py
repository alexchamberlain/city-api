import pkgutil

from .util import make_executable_schema, parse_schema, loader_resolver, get_loader
from .loaders import CountryLoader


async def city_resolver(context, resolve_info, *, name=None, geonameID=None):
    loader = get_loader(resolve_info, 'City')

    if geonameID is not None:
        return loader.geoname_id_load(geonameID)
    elif name is not None:
        return loader.name_load(name)


def country_cities_resolver(country, resolve_info):
    loader = get_loader(resolve_info, 'City')
    return loader.country_iso_load(country.iso)


def build_schema():
    data = pkgutil.get_data('cities', 'cities.graphql').decode()
    schema = make_executable_schema(
        parse_schema(data),
        {
            'Query': {
                'country': loader_resolver('Country', CountryLoader.resolver),
                'city': city_resolver
            },
            'Country': {
                'cities': country_cities_resolver
            },
            'City': {
                'country': loader_resolver('Country', CountryLoader.context_resolver)
            }
        }
    )

    return schema
