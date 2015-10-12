
version = '0.1.0'

def execute(sequence_nodes):

    num_trials = 0
    num_converged = 0

    for node in sequence_nodes:
        num_trials += node['output']['num_trials']
        num_converged += node['output']['num_converged']

    return {
        'num_trials': len(saccade_nodes),
        'num_converged': num_converged,
    }
