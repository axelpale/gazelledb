
version = '0.2.0'

def execute(saccade_nodes):

    trial_conf_id = saccade_nodes[0]['output']['trial_configuration_id']

    num_converged = 0
    nonconvergent_trials = []

    for node in saccade_nodes:
        if node['output']['did_converge']:
            num_converged += 1
        else:
            nonconvergent_trials.append(node['name'])

    return {
        'trial_configuration_id': trial_conf_id,
        'num_trials': len(saccade_nodes),
        'num_converged': num_converged,
        'nonconvergent_trials': nonconvergent_trials,
    }
