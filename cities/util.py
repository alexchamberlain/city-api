import functools

from graphql import build_ast_schema
from graphql.language.parser import parse
from graphql.type.definition import GraphQLObjectType, GraphQLScalarType


def parse_schema(document):
    return build_ast_schema(parse(document))


def make_executable_schema(schema, resolvers):
    for type_name, type_resolver in resolvers.items():
        type_ = schema.get_type(type_name)

        if isinstance(type_, GraphQLObjectType):
            for field_name, field_resolver in type_resolver.items():
                type_.fields[field_name].resolver = field_resolver
        elif isinstance(type_, GraphQLScalarType):
            type_.description = type_resolver.get('description')
            type_.serialize = type_resolver.get('serialize')
            type_.parse_value = type_resolver.get('parse_value')
            type_.parse_literal = type_resolver.get('parse_literal')

    return schema


def loader_resolver(object_type, unbound_method):
    @functools.wraps(unbound_method)
    def _(context, resolve_info, **kwargs):
        loader = get_loader(resolve_info, object_type)
        return unbound_method(loader, context, resolve_info, **kwargs)

    return _


def get_loader(resolve_info, object_type):
    if 'request' in resolve_info.context:
        return resolve_info.context['request']['loaders'][object_type]
    else:
        return resolve_info.context['loaders'][object_type]
