# -*- coding: utf-8 -*-
import os, pkginfo, datetime, time

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
pkg_info = pkginfo.Develop(os.path.join(os.path.dirname(__file__),'..'))
build_date = datetime.datetime.utcfromtimestamp(int(os.environ.get('SOURCE_DATE_EPOCH', time.time())))

intersphinx_mapping = {'http://docs.python.org': None}

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx'
    ]

# General
source_suffix = '.rst'
master_doc = 'index'
project = pkg_info.name
copyright = '2016 - %s Chris Withers' % build_date.year
version = release = pkg_info.version
exclude_patterns = [
    'description.rst',
    '_build'
]
pygments_style = 'sphinx'

# Options for HTML output
html_theme = 'default' if on_rtd else 'classic'
htmlhelp_basename = project+'doc'

# Options for LaTeX output
latex_documents = [
  ('index',project+'.tex', project+u' Documentation',
   'Chris Withers', 'manual'),
]

