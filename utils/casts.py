from .functions import haskey

def try_get(obj, name):
    if hasattr(obj, 'app_label'):
        return True, obj.app_label
    if haskey(obj, 'app_label'):
        return True, obj['app_label']
    return False, obj
