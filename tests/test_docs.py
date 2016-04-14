from doctest import REPORT_NDIFF, ELLIPSIS
from glob import glob
from os.path import dirname, join, pardir

from manuel import doctest, capture, codeblock
from manuel.testing import TestSuite

root = join(dirname(__file__), pardir)
tests = glob(join(root, 'docs', '*.rst'))
tests.append(join(root, 'README.rst'))

def test_suite():
    m =  doctest.Manuel(optionflags=REPORT_NDIFF|ELLIPSIS)
    m += codeblock.Manuel()
    m += capture.Manuel()
    return TestSuite(m, *tests)
