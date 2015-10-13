
version = '0.2.0'

def execute(session_nodes):

    num_trials = 0
    num_converged = 0
    nonconvergent_trials = []

    for node in session_nodes:
        num_trials += node['output']['num_trials']
        num_converged += node['output']['num_converged']
        nonconvergent_trials += node['output']['nonconvergent_trials']

    return {
        'num_trials': num_trials,
        'num_converged': num_converged,
        'nonconvergent_trials': nonconvergent_trials,
    }
