from ast import literal_eval
from setuptools import setup, find_packages

def get_version(source='lib/json_ldq/__init__.py'):
    with open(source) as f:
        for line in f:
            if line.startswith('__version__'):
                return literal_eval(line.partition('=')[2].lstrip())
    raise ValueError("VERSION not found")

README = ''
with open('README.rst', 'r') as f:
    README = f.read()

setup(
    name='JSON-LDQ',
    version = get_version(),
    package_dir = {'': 'lib'},
    packages = find_packages(where='lib'),
    description='A JSON-based query language for Linked Data',
    long_description = README,
    author='Pierre-Antoine Champin',
    #author_email='TODO',
    license='LGPL v3',
    #url='TODO',k
    platforms='OS Independant',
    install_requires = ["rdflib", "pyld"],
    tests_require = ["nose"],
    test_loader = 'nose.loader:TestLoader',
    test_suite='utests',
)