# -*- coding: utf-8 -*-
import os, datetime, time
from importlib import metadata

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
build_date = datetime.datetime.utcfromtimestamp(int(os.environ.get('SOURCE_DATE_EPOCH', time.time())))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    ]

intersphinx_mapping = {
    'python': ('http://docs.python.org', None),
    'sqlalchemy': ('https://docs.sqlalchemy.org/en/20/', None),
}


# General
source_suffix = '.rst'
master_doc = 'index'
project = 'chide'
copyright = '2016 - %s Chris Withers' % build_date.year
version = release = metadata.version(project)
exclude_trees = ['_build']
pygments_style = 'sphinx'

# Options for HTML output
html_theme = 'furo'
htmlhelp_basename = project+'doc'

# Options for LaTeX output
latex_documents = [
  ('index',project+'.tex', project+u' Documentation',
   'Chris Withers', 'manual'),
]

nitpicky = True
nitpick_ignore = [
    ('py:class', 'Address'),  # documentation example
    ('py:func', 'identify'),  # documentation example
]
