try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Screeps Console',
    'author': 'Robert Hafner',
    'url': 'https://github.com/tedivm/screeps_console',
    'download_url': 'https://github.com/tedivm/screeps_console/releases',
    'author_email': 'tedivm@tedivm.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['screeps_console'],
    'scripts': [],
    'entry_points': {'console_scripts': ['screepsconsole = screeps_console.interactive:main']},
    'name': 'screeps_console'
}

setup(**config)
