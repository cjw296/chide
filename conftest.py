from doctest import REPORT_NDIFF, ELLIPSIS

from sybil import Sybil
from sybil.parsers.rest import DocTestParser, PythonCodeBlockParser, CaptureParser


pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(optionflags=REPORT_NDIFF|ELLIPSIS),
        PythonCodeBlockParser(),
        CaptureParser(),
    ],
    pattern='*.rst',
).pytest()
