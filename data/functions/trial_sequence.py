
version = '0.1.0'

def execute(saccade_nodes):

    num_converged = 0

    for node in saccade_nodes:
        if node['output']['did_converge']:
            num_converged += 1

    return {
        'num_trials': len(saccade_nodes),
        'num_converged': num_converged,
    }
