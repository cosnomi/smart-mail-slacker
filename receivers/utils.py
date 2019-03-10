from datetime import datetime


class MessageData:
    keys = [('internal_date', datetime), ('subject', str), ('body', str),
            ('from', list), ('to', list)]

    def __init__(self, params):
        for key, expected_type in self.keys:
            if not key in params:
                raise KeyError(key)
            if not isinstance(params[key], expected_type):
                raise TypeError('expected {} to be {}, but got {}'.format(
                    key, expected_type, type(params[key])))
            setattr(self, key, params[key])

    def get_value(self, key):
        if key not in [x[0] for x in self.keys]:
            raise KeyError(key)
        return getattr(self, key)