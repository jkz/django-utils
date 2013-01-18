from django.db import transaction

class NestingTransaction(object):
    _savepoints = []

    def __init__(self, using=None):
        self.using = using
            
    def is_open(self):
        return not self._savepoints

    @classmethod
    def push(cls, sid):
        cls._savepoints.append(sid)

    @classmethod
    def pop(cls):
        return cls._savepoints.pop()

    @classmethod
    def peek(cls):
        return cls._savepoints[-1]

    def rollback(self):
        sid = self.peek()
        transaction.savepoint_rollback(sid)

    def __enter__(self):
        if not self.is_open():
            transaction.enter_transaction_management(self.using)
        sid = transaction.savepoint()
        self.push(sid)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        sid = self.pop()
        if not self.is_open():
            transaction.savepoint_commit(sid)
            transaction.leave_transaction_management(self.using)
