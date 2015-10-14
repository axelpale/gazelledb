from numpy import mean

version = '0.2.2'

def execute(saccade_nodes):

    trial_conf_id = saccade_nodes[0]['output']['trial_configuration_id']

    num_converged = 0
    nonconvergent_trials = []

    for node in saccade_nodes:
        if node['output']['did_converge']:
            num_converged += 1
        else:
            nonconvergent_trials.append(node['name'])

    # Average validity ratio
    mean_validity_ratio = mean([n['output']['validity_ratio'] for n in saccade_nodes])

    return {
        'trial_configuration_id': trial_conf_id,
        'mean_validity_ratio': mean_validity_ratio,
        'num_trials': len(saccade_nodes),
        'num_converged': num_converged,
        'nonconvergent_trials': nonconvergent_trials,
    }
