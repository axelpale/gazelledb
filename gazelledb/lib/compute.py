from importlib import import_module

# For update times
from time import time as unix_timestamp

# Enable custom node function import
import sys, os
dup = os.path.dirname
env_root = dup(dup(dup(__file__)))
sys.path.append(os.path.join(env_root, 'data'))

import get_node

class InvalidNodeError(Exception):
    pass

class InvalidNodeFunctionError(Exception):
    pass

class InvalidNodeFunctionAPIError(Exception):
    pass

def compute_node(db, node, policy='init'):
    '''
    Ensure that node is up-to-date and if not then execute it's function.
    Return the ensured node.

    Computation policies:
      policy='init' (default)
        compute only if not computed before.
      policy='ensure'
        ensure that cache is up-to-date and execute only if necessary.
      policy='force'
        compute always, disregard any caches.
    '''
    print 'Computing node: ' + node['name']
    #import pdb; pdb.set_trace()

    if policy not in ['init', 'ensure', 'force']:
        raise ValueError('Unknown policy: ' + policy)

    # Node might not have been found
    if node is None:
        raise InvalidNodeError('Invalid node: None')

    # Ensure that the object really has sufficient properties
    if any(map(lambda x: x not in node, ['name', 'function', 'output'])):
        raise InvalidNodeError('Node does not have required attributes.')

    # Aliases to simplify names.
    input_names = node['input']
    input_times = node['input_timestamp']
    fn_versions = node['function_version']
    output      = node['output']
    fn_names    = node['function']

    # Ensure that the object really has sufficient properties
    if not isinstance(fn_versions, list):
        raise InvalidNodeError('Node\'s function versions should be a list.')
    if not isinstance(fn_names, list):
        raise InvalidNodeError('Node\'s function should be a list.')

    # Node without function is a data node, and does not need execution
    if len(fn_names) < 1:
        # A data node, no functions to execute
        return node

    # If node has been run before, return it without recomputation
    if policy == 'init' and len(fn_versions) == len(fn_names):
        return node

    # Gather the data for execution. Load input nodes:
    input_nodes = map(lambda n: get_node.by_name_computed(db, n, policy), input_names)

    # Import functions.
    fn_modules = []
    for fn_name in fn_names:

        # Import the function
        try:
            modu = import_module('functions.' + fn_name)
        except ImportError as e:
            raise InvalidNodeFunctionError('No node function ' + fn_name +
              ' can be found or there is problem in the module: ' + str(e))

        # Assert: import successful
        if not hasattr(modu, 'execute') or not hasattr(modu, 'version'):
            raise InvalidNodeFunctionAPIError('Node function should have an ' +
            'execute method and version property.')

        fn_modules.append(modu)

    # If the function versions have remained the same
    # and cached output has same timestamp as the input nodes,
    # then do not recompute. However, under 'force' policy, compute
    # anyway. Under 'init' policy, if we got this far, nothing is up-to-date.
    if policy != 'force':
        if len(input_times) == len(input_nodes): # Test if virgin
            if all(map(lambda nt: nt[0]['timestamp'] == nt[1],
                       zip(input_nodes, input_times))):
                # Output is up to date
                if len(fn_names) == len(fn_versions):
                    if all(map(lambda fv: fv[0].version == fv[1],
                               zip(fn_modules, fn_versions))):
                        # no reason to recompute
                        return node

    # Execute functions from left to right, feeding the prev output to
    # next input. Give input nodes as parameters to the first.
    input_args = input_nodes
    for modu in fn_modules:
        # Execute the function TODO function composition
        input_args = modu.execute(input_args)
    # The last input_args is the final output.

    # Store results and update timestamps. Like a cache.
    node['output'] = input_args
    node['timestamp'] = int(unix_timestamp())
    node['input_timestamp'] = map(lambda n: n['timestamp'], input_nodes)
    node['function_version'] = map(lambda m: m.version, fn_modules)

    #pdb.set_trace()
    db.nodes.replace_one({'_id': node['_id']}, node)

    return node
