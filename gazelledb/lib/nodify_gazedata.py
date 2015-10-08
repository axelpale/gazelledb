# For path handling
import os

# For creation times
from time import time as unix_timestamp

# Import igazelib
import sys
igazelib_root = '/Users/xeli/Dropbox/build/icl-trial-variability/gazedata'
sys.path.append(igazelib_root)
from igazelib import loadjson, loadCsvAsJson
from igazelib import gazedata, protocol as pr

# For gazedata filename patterns
from gazedatafilenamerecognizer import GazedataFilenameRecognizer
rec = GazedataFilenameRecognizer()


def combine_eyes(rx, ry, lx, ly):
    '''
    Return x, y
    '''
    if rx == -1.0:
        if lx == -1.0:
            x = None
        else:
            x = lx
    else:
        if lx == -1.0:
            x = rx
        else:
            # Both valid
            x = 0.5 * lx + 0.5 * rx

    if ry == -1.0:
        if ly == -1.0:
            y = None
        else:
            y = ly
    else:
        if ly == -1.0:
            y = ry
        else:
            # Both valid
            y = 0.5 * ly + 0.5 * ry
    return x, y


def tobii_to_gazelle(tobii_gazepoint):
    # Transform to Gazelle v0.1.0
    gp = tobii_gazepoint  # alias
    rx = float(gp[pr.rxkey])
    ry = float(gp[pr.rykey])
    lx = float(gp[pr.lxkey])
    ly = float(gp[pr.lykey])
    x, y = combine_eyes(rx, ry, lx, ly)

    return {
        'time_mics': int(gp[pr.timekey]),
        'gaze_x': x,
        'gaze_y': y,
    }


def convert_to_trial_nodes(gazedata_path, config_path):
    '''
    Return
      list of nodes
    '''
    # Open file
    config = loadjson(config_path)

    g = loadCsvAsJson(gazedata_path, dialect='excel-tab')
    # Collect meta from filename
    meta = rec.recognize_from_filename(gazedata_path)
    # Pick config id from filemeta
    config_id = meta['trial_configuration_id']
    # Pick meta from config. Find correct config by config id.
    trialseq_config = filter(lambda x: x['name'] == config_id,
                             config)[0]
    aoi_rects = trialseq_config['aois']

    # Create entries (and collections) for each + entry for source file

    # For each trial, create a trial node
    trials = gazedata.getTrials(g)
    nodes = []
    for trial in trials:

        # Collect trial meta
        relevant_g = gazedata.getSaccadeWindow(trial)
        rel_start, rel_end = gazedata.getSaccadeWindowRange(trial)
        aoi_xy = gazedata.getTargetLocation(relevant_g, aoi_rects)
        num_valid_p = gazedata.countValidGazepoints(trial)
        num_valid_sac_p = gazedata.countValidGazepoints(relevant_g)
        if len(trial) > 0:
            validity_ratio = float(num_valid_p) / len(trial)
        else:
            validity_ratio = 0

        trial_num = gazedata.getTrialNumber(trial)
        trial_num_str = str(trial_num).zfill(2)
        age_str = str(meta['participant_age_months']) + 'mo'

        # Normalize gazepoints
        norm_g = map(tobii_to_gazelle, trial)

        name_root = '/'.join([
            'icl',
            'cg',
            'person',
            meta['participant_id'],
            'age',
            age_str,
            'method',
            meta['method_version'],
            meta['trial_configuration_id'].lower(),
            'trial',
            trial_num_str,
        ])

        trial_node = {
            'name': name_root + '/',
            'timestamp': int(unix_timestamp()),
            'format': 'gazelle/v1/trial/simple/',
            'meta': {
                'date': gazedata.get_trial_date(trial),
                'participant_id': meta['participant_id'],
                'method_version': meta['method_version'],
                'participant_age_months': meta['participant_age_months'],
                'calibration_successful': meta['calibration_successful'],
                'trial_configuration_id': meta['trial_configuration_id'],
                'trial_number': trial_num,
                'num_points': len(norm_g),
                'num_valid_points': num_valid_p,
                'validity_ratio': validity_ratio,
                'aoi_x_rel': aoi_xy[0],
                'aoi_y_rel': aoi_xy[1],
                'source_file': os.path.basename(gazedata_path),
                'tags': {
                    'target': {'range': [rel_start, -1]},
                    'saccade_window': {'range': [rel_start, rel_end]},
                },
            },
            'function': [],
            'function_version': [],
            'input': [],
            'input_timestamp': [],
            'output': norm_g,
        }

        nodes.append(trial_node)
    return nodes

def convert_to_saccade_node(trial_node):
    n = trial_node
    return {
        'name': n['name'] + 'saccade/',
        'timestamp': int(unix_timestamp()),
        'format': 'gazelle/v1/saccade/',
        'meta': {},
        'function': ['saccade_em'],
        'function_version': [],  # virgin
        'input': [n['name']],
        'input_timestamp': [],  # virgin
        'output': [],  # virgin
    }

def convert_to_trial_sequence_node(saccade_nodes):
    '''
    Combine trial nodes
    '''
    if len(saccade_nodes) < 1:
        return

    # prototype that gives us the common meta
    sacc_name = saccade_nodes[0]['name']
    node_name = '/'.join(sacc_name.split('/')[:-4]) + '/'

    return {
        'name': node_name,
        'timestamp': int(unix_timestamp()),
        'format': 'gazelle/v1/sequence/simple/',
        'meta': {},
        'function': ['trial_sequence'],
        'function_version': [],  # virgin
        'input': map(lambda n: n['name'], saccade_nodes),
        'input_timestamp': [],  # virgin
        'output': [],  # virgin
    }
