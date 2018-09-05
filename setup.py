from setuptools import setup


setup(
    name='sparrow',
    version='0.0.1',
    description='',
    license='BSD',
    packages=['sparrow'],
    install_requires=[
        'Django>=2.1',
        'djangorestframework>=3.8',
        'python-decouple',
        'psycopg2',
        'dj-database-url',
        'python-dateutil',
    ]
)
