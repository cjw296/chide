from typing import Any


class Comparable:

    def __repr__(self) -> str:
        return '<{}: {}>'.format(
            type(self).__name__,
            ', '.join(k+'='+repr(v) for (k, v) in sorted(vars(self).items()))
        )

    def __eq__(self, other: Any) -> bool:
        self_vars = dict((k, v) for (k, v) in vars(self).items()
                         if not k.startswith('_'))
        other_vars = dict((k, v) for (k, v) in vars(other).items()
                         if not k.startswith('_'))
        return type(self) is type(other) and self_vars == other_vars
