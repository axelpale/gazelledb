# For creation times
from time import time as unix_timestamp

class InvalidNodeCandidate(Exception):
    pass

def by_prototype(baby_node):
    '''
    Generates valid node from minimal node dictionary.
    Required keys are 'name' and 'format'.
    '''
    b = baby_node  # alias
    adult_node = {}

    required_keys_and_types = {
        'name': str,
        'format': str
    }

    keys_and_defaults = {
        'function': [],
        'function_version': [],
        'input': [],
        'input_timestamp': [],
        'function_version': [],
        'output': None,
        'meta': {},
        'timestamp': int(unix_timestamp()),
    }

    for k, t in required_keys_and_types.items():
        if k not in b:
            raise InvalidNodeCandidate('Node does not have required keys.')
        if isinstance(b[k], t):
            raise InvalidNodeCandidate('Node key ' + k + ' has invalid type.')
        adult_node[k] = b[k]

    for k, default in keys_and_defaults.items():
        if k in baby_node:
            adult_node[k] = baby_node[k]
        else:
            adult_node[k] = default

    return adult_node
