from importlib import import_module
import get_node

class InvalidNodeError(Exception):
    pass

class InvalidNodeFunctionError(Exception):
    pass

class InvalidNodeFunctionAPIError(Exception):
    pass

def compute_node(db, node):
    '''
    Ensure that node is up-to-date and if not then execute it's function.
    Return the ensured node.
    '''
    print 'Computing node: ' + node['name']

    if node is None:
        raise InvalidNodeError('Invalid node: None')

    if any(map(lambda x: x not in node, ['name', 'function', 'output'])):
        raise InvalidNodeError('Node does not have required attributes.')

    input_names = node['input']
    input_times = node['input_timestamp']
    fn_versions = node['function_version']
    output = node['output']
    fn_names   = node['function']

    if not isinstance(output, list):
        raise InvalidNodeError('Node\'s output should be a list.')
    if not isinstance(fn_names, list):
        raise InvalidNodeError('Node\'s function should be a list.')


    if len(fn_names) < 1:
        # A data node, no functions to execute
        return node

    # Load input nodes:
    input_nodes = map(lambda n: get_node.by_name_computed(db, n), input_names)

    # Import functions. If the function versions have remainded the same
    # and inputs are up to date, then no reason to recompute.
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

    # If cached inputs and functions are up to date then no reason to recompute.
    if len(input_times) == len(input_nodes): # Test if virgin
        if all(map(lambda n, t: n['timestamp'] == t,
                   zip(input_nodes, input_times))):
            # Output is up to date
            if len(fn_names) == len(fn_versions):
                if all(map(lambda f, v: f.version == v,
                           zip(fn_modules, fn_versions))):
                    # no reason to recompute
                    return node


    # Execute functions from left to right, feeding the prev output to
    # next input. Give input nodes as parameters to the first.
    input_args = input_nodes

    for modu in fn_modules:
        # Execute the function TODO function composition
        input_args = modu.execute(input_args)

    # Store results and update timestamps. Like a cache.
    node['output'] = input_args
    node['input_timestamp'] = map(lambda n: n['timestamp'], input_nodes)
    node['function_version'] = map(lambda m: m.version, fn_modules)
    db.collection.save(node)

    return node
