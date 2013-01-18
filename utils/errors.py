class StatusError(Exception):
    code = 'error'

    def __init__(self, source=None, message=None):
        self.source = source
        self.message = message

    def data(self):
        return {'code': self.code,
                'message': self.message,
                'source': self.source}

    def __str__(self):
        return '%s | %s: %s' % (self.code, self.source, self.message)

class CastError(TypeError):
    def __init__(self, old, new, note=''):
        Exception.__init__(self)
        self.old = old
        self.new = new
        self.note = note

    def __str__(self):
        self.msg = 'CastError: Attempted to cast %s to %s%s' % (
                self.old, self.new, self.note and ' (%s)' % self.note)

