import re

def r(regex):
    """
    Replace `:name` and `#number` by named groups of respective types

    >>> r(r'/:name/#number/(?:name)/')
    '/(?P<name>[^/]+)/(?P<number>[0-9]+)/(?:name)/'
    """

    def name_repl(match):
        grp = match.group(0)
        if grp.startswith('(?'):
            return grp
        else:
            return r'(?P<{}>[^/]+)'.format(match.group(0).lstrip(':'))
    regex = re.sub(r'((?:\(\?|):[a-zA-Z_][a-zA-Z_0-9]*)', name_repl, regex)

    def number_repl(match):
        return r'(?P<{}>[0-9]+)'.format(match.group(0).lstrip('#'))
    regex = re.sub(r'#([a-zA-Z_][a-zA-Z_0-9]*)', number_repl, regex)

    return regex


if __name__ == "__main__":
    import doctest
    doctest.testmod()

