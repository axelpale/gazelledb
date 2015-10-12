
version = '0.1.0'

def execute(saccade_nodes):

    trial_conf_id = saccade_nodes[0]['output']['trial_configuration_id']

    num_converged = 0

    for node in saccade_nodes:
        if node['output']['did_converge']:
            num_converged += 1

    return {
        'trial_configuration_id': trial_conf_id,
        'num_trials': len(saccade_nodes),
        'num_converged': num_converged,
    }
