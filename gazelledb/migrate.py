# -*- coding: utf-8 -*-
'''
Generate a hierarchy of nodes from ICL gazedata

'''
import os
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
import pprint
from lib.nodify_gazedata import convert_to_trial_nodes, convert_to_saccade_node, convert_to_trial_sequence_node, convert_to_session_node, convert_to_project_node
from lib.gazedatafilenamerecognizer import GazedataFilenameRecognizer

# Directory of source gazefiles
gazedata_root = '/Users/xeli/Dropbox/build/icl-trial-variability/gazedata'
source_dir = os.path.join(gazedata_root, 'CG-8mo-raw')
# Config data (trial description)
config_path = os.path.join(gazedata_root, 'CG-8mo-raw',
                           'cg_8_tbt-trial-config.json')

# Database client
mongo = MongoClient()  # Default port @ localhost
# Clear db
mongo.drop_database('gazelle')
# Initialize db
db = mongo.gazelle
db.nodes.create_index('name', unique=True)

# Trial sessions. Identified by participant, age, and calibration
sequences_per_session = {}

# For each gazedata file aka trial sequence
i = 0
for file_name in os.listdir(source_dir):
    if not file_name.endswith('.gazedata'):
        continue

    # if i > 1:
    #     break
    # i += 1


    # Convert to trial nodes
    source_path = os.path.join(source_dir, file_name)
    trial_nodes = convert_to_trial_nodes(source_path, config_path)
    saccade_nodes = map(convert_to_saccade_node, trial_nodes)

    # Cancel processing the file if no trials found.
    # This can happen if gazedata file is short
    if len(saccade_nodes) < 1:
        print 'Notice: no saccade trials were found from ' + file_name
        print 'Skipping to next file...'
        continue

    # Convert to trial sequence
    trial_sequence_node = convert_to_trial_sequence_node(saccade_nodes)

    # Add sequence to session. Sequences can come in any order
    rec = GazedataFilenameRecognizer()
    filename_meta = rec.recognize_from_filename(file_name)
    p_id = filename_meta['participant_id']
    p_age = str(filename_meta['participant_age_months'])
    p_calib = 'calib' if filename_meta['calibration_successful'] else 'nocalib'
    session_id = '/'.join([p_id, p_age, p_calib]) + '/'
    trial_conf_id = filename_meta['trial_configuration_id']
    if session_id not in sequences_per_session:
        sequences_per_session[session_id] = {}
    sequences_per_session[session_id][trial_conf_id] = trial_sequence_node

    # Insert nodes to database but first see if any trials found.
    if len(trial_nodes) > 0:
        try:
            db.nodes.insert_many(trial_nodes + saccade_nodes + [trial_sequence_node])
        except BulkWriteError as err:
            errs = err.details.writeErrors
            for e in errs:
                print e['errmsg']

# Order sequences inside sessions to time order.
for session_id, sess in sequences_per_session.iteritems():
    # sess is a dict of sequences. Order by keys:
    #import pdb; pdb.set_trace()
    sorted_seq_tuples = sorted(sess.items(), key=lambda kv: kv[0])
    sorted_seq = map(lambda kv: kv[1], sorted_seq_tuples)
    sequences_per_session[session_id] = sorted_seq

# For each session
session_nodes = map(convert_to_session_node, sequences_per_session.values())
db.nodes.insert_many(session_nodes)

# For each project
project_node = convert_to_project_node(session_nodes)
db.nodes.insert_one(project_node)
