# -*- coding: utf-8 -*-
import os
from pymongo import MongoClient
from lib.nodify_gazedata import convert_to_nodes

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

# For each gazedata file
i = 0
for file_name in os.listdir(source_dir):
    if not file_name.endswith('.gazedata'):
        continue

    # if i > 1:
    #     break
    # i += 1

    # Convert to node
    source_path = os.path.join(source_dir, file_name)
    trial_nodes = convert_to_nodes(source_path, config_path)

    # See if trials found
    if len(trial_nodes) > 0:
        db.nodes.insert_many(trial_nodes)
