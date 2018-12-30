from .model import StringModel

class LockProcessCache(StringModel):
    def __init__(self, func_name, is_load=False):
        key = 'lock_process:{func_name}'.format(func_name=func_name)
        super(LockProcessCache, self).__init__(key, is_load)
