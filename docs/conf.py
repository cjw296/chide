from importlib import metadata

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python': ('http://docs.python.org', None),
    'sqlalchemy': ('https://docs.sqlalchemy.org/en/20/', None),
    'testfixtures': ('https://testfixtures.readthedocs.io/en/latest/', None),
}


# General
source_suffix = '.rst'
master_doc = 'index'
project = 'chide'
copyright = '2016 onwards Chris Withers'
version = release = metadata.version(project)
exclude_trees = ['_build']
pygments_style = 'sphinx'
autodoc_member_order = 'bysource'

# Options for HTML output
html_theme = 'furo'
htmlhelp_basename = project + 'doc'

nitpicky = True
nitpick_ignore = [
    ('py:class', 'Address'),  # documentation example
    ('py:class', 'chide.collection.T'),  # type var
    ('py:class', 'chide.factory.T'),  # type var
    ('py:obj', 'chide.factory.T'),  # type var
    ('py:class', 'chide.set.T'),  # type var
    ('py:class', 'chide.markers.T'),  # type var
    ('py:obj', 'chide.markers.T'),  # type var
    ('py:class', 'chide.simplifiers.T'),  # type var
    ('py:obj', 'chide.simplifiers.T'),  # type var
    ('py:func', 'identify'),  # documentation example
]
