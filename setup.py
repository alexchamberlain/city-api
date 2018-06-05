from setuptools import setup

setup(
    name='cities',
    version='0.1',
    description='City API: GraphQL Example Server',
    packages=['cities'],
    package_data={'cities': ['cities.graphql']},
    install_requires=[
        'aiodataloader',
        'asyncpg',
        'attrs',
        'graphql-core==2.1rc1',
        'sanic',
        'sanic-graphql'
    ]
)
