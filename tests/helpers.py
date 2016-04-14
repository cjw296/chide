class Comparable:

    def __repr__(self):
        return '<{}: {}>'.format(
            type(self).__name__,
            ', '.join(k+'='+repr(v) for (k, v) in sorted(vars(self).items()))
        )

    def __eq__(self, other):
        return type(self) is type(other) and vars(self)==vars(other)
