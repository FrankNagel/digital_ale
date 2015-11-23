import os

from setuptools import setup, find_packages
import multiprocessing

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'pyramid_mailer',
    'SQLAlchemy',
    'psycopg2',
    'alembic',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'cryptacular',
    'pycrypto',
    ]

setup(name='digital_ale',
      version='0.0',
      description='digital_ale',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='digital_ale',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = digital_ale:main
      [console_scripts]
      initialize_digital_ale_db = digital_ale.scripts.initializedb:main
      ale_insert_concept = digital_ale.scripts.insert_concept:main
      ale_import_files = digital_ale.scripts.import_files:main
      ale_import_places = digital_ale.scripts.import_places:main
      ale_merge_geodata = digital_ale.scripts.merge_geodata:main
      ale_sanitize1 = digital_ale.scripts.sanitize1:main
      ale_make_replacements = digital_ale.scripts.make_replacements:main
      """,
      )
