# Gazelle Database

Open database for scientific gaze data.

Akseli Palén
Infant Cognition Laboratory
University of Tampere

## Install

    $ virtualenv gazelledb
    $ cd gazelledb
    $ source bin/activate
    (env)$ pip install flask
    (env)$ pip install pymongo
    (env)$ pip install numpy
    (env)$ pip install coloredlogs

## Run

First, start MongoDB database server:

    $ cd project/root/path
    $ mongod --config data/mongodb.conf

Then, activate the virtual Python environment and start the web server:

    $ source bin/activate
    (env)$ python gazelledb/server.py

If you want to shut down the web server, close it and exit the environment:

    [press ctrl-c]
    (env)$ deactivate

Optionally you can also open Mongo console:

    $ mongo

## Examples

Trial gaze points

{
    'name': name_root + '/',
    'timestamp': 123456789,
    'format': 'gazelle/v1/trial',
    'meta': {
        'date': gazedata.get_trial_date(trial),
        'participant_id': meta['participant_id'],
        'method_version': meta['method_version'],
        'participant_age_months': meta['participant_age_months'],
        'calibration_successful': meta['calibration_successful'],
        'trial_configuration_id': meta['trial_configuration_id'],
        'trial_number': trial_num,
        'aoi_x_rel': aoi_xy[0],
        'aoi_y_rel': aoi_xy[1],
        'source_file': file,
        'tags': {
            'target': {
                'range': [100, -1]
                'meta': {
                    ...
                }
            },
            'first_and_second': {
                'include': [0, 1]
            },
            'last': {
                'include': [-1]
            },
            'saccade': {
                'range': [678, 789]
            }
        }
    },
    'function': [],
    'input': [],
    'input_timestamp': [],
    'output': norm_g
}

Trial analysis

{
    'name': icl/trial/analysis,
    'timestamp': 1233456789,
    'format': 'gazelle/v1/saccade', // Description
    'meta': {},
    'function': ['analysis.py'],
    'input': string or list or pattern
        ['icl/name@123456789', '...@...', 'name@time']
    'input_timestamp': { // Check if newer
        'icl/name@123456789': 123456789,
        'icl/name2': 123456788
    }// or list, keys are in the input
    'output': a list in format gazelle/v1/saccade
}

Trial analysis merging

{
    'name': 'icl/sequence',
    'timestamp': 1233456789,
    'format': 'gazelle/v1/saccades',
    'meta': {},
    'function': 'merge-analysis.py',
    'input': ['icl/trial', 'icl/trial2'],
    'output': list in format gazelle/v1/saccades
}

Prediction analysis

{
    'name': ...,
    'timestamp': 11111111111,
    'format': 'gazelle/v1/prediction',
    'meta': {},
    'function': 'prediction-analysis.py',
    'input': ['icl/sequence'],
    'input_timestamp': [1234567678],
    'output': {
        'probabilities': ... how they affect reaction time, LATER model
    }
}
