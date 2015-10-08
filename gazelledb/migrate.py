# -*- coding: utf-8 -*-
import os
from pymongo import MongoClient
from lib.nodify_gazedata import convert_to_trial_nodes, convert_to_saccade_node, convert_to_trial_sequence_node

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

    # Convert to trial sequence
    trial_sequence_node = convert_to_trial_sequence_node(saccade_nodes)

    # See if trials found
    if len(trial_nodes) > 0:
        db.nodes.insert_many(trial_nodes + saccade_nodes + [trial_sequence_node])
