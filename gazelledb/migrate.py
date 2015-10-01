# -*- coding: utf-8 -*-

import os
import re
from time import time as unix_timestamp
from pymongo import MongoClient

import sys
dup = os.path.dirname
project_root = dup(dup(__file__))
gazedata_root = '/Users/xeli/Dropbox/build/icl-trial-variability/gazedata'
sys.path.append(gazedata_root)
from igazelib import loadjson, loadCsvAsJson
from igazelib import gazedata, protocol as pr

# Directory of source gazefiles
source_dir = os.path.join(gazedata_root, 'CG-8mo-raw')
# Pattern of gazefile filenames
fileregexp = 'cg(\d+)_(\d+[a-z]?)_childcogn_(\d)m(NoCalib)?_SRT(\d)'
patt = re.compile(fileregexp)
# Database client
mongo = MongoClient() # Default port @ localhost
# Clear db
mongo.drop_database('gazelle')
# Initialize db
db = mongo.gazelle

# Config data (trial description)
config_path = os.path.join(gazedata_root, 'CG-8mo-raw',
                           'cg_8_tbt-trial-config.json')
config = loadjson(config_path)

def recognizeName(file):
	# Recognize metadata from filename
	bn = os.path.basename(file)
	m = patt.match(bn)
	return {
		'participant_id': m.group(1).zfill(4),
		'method_version': m.group(2),
		'participant_age_months': int(m.group(3)),
		'calibration_successful': (m.group(4) == None),
		'trial_configuration_id': 'SRT' + m.group(5)
	}

def generate_trial_ID(trial_meta):
	# Unique key for a trial
	m = trial_meta # alias
	year = m['date'][:4]
	auth = 'fi-uta-icl'
	proj = year + '-8mo'
	p = 'p' + m['participant_id']
	v = 'v' + m['method_version'] + '-' + m['trial_configuration_id']
	n = 't' + str(m['trial_number']).zfill(2)
	return '_'.join([auth, proj, p, v, n])

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
	gp = tobii_gazepoint # alias
	rx = float(gp[pr.rxkey])
	ry = float(gp[pr.rykey])
	#rv = int(gp[pr.rvkey])
	lx = float(gp[pr.lxkey])
	ly = float(gp[pr.lykey])
	#lv = int(gp[pr.lvkey])
	x, y = combine_eyes(rx, ry, lx, ly)

	return {
		'time_mics': int(gp[pr.timekey]),
		'gaze_x': x,
		'gaze_y': y,
	}

# For each gazedata file
i = 0
for file in os.listdir(source_dir):
	if not file.endswith('.gazedata'):
		continue

	# if i > 1:
	# 	break
	# i += 1

	# Open file
	source_path = os.path.join(source_dir, file)
	g = loadCsvAsJson(source_path, dialect='excel-tab')
	# Collect meta from filename
	meta = recognizeName(file)
	# Pick config id from filemeta
	config_id = meta['trial_configuration_id']
	# Pick meta from config. Find correct config by config id.
	trialseq_config = filter(lambda x: x['name'] == config_id,
	                         config)[0]
	aoi_rects = trialseq_config['aois']

	# Create entries (and collections) for each + entry for source file

	# For each trial, create a trial document
	trials = gazedata.getTrials(g)
	for trial in trials:

		# Collect trial stats
		relevant_g = gazedata.getSaccadeWindow(trial)
		rel_start, rel_end = gazedata.getSaccadeWindowRange(trial)
		aoi_xy = gazedata.getTargetLocation(relevant_g, aoi_rects)

		trial_num = gazedata.getTrialNumber(trial)
		trial_num_str = str(trial_num).zfill(2)
		age_str = str(meta['participant_age_months']) + 'mo'

		# Normalize gazepoints
		norm_g = map(tobii_to_gazelle, g)

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

		# Target first second
		# When queried, will return the referenced data
		db.nodes.insert_one({
			'name': '/'.join([name_root, 'saccade', '']),
			'timestamp': int(unix_timestamp()),
			'format': 'gazelle/v1/saccade/',
			'meta': {
				'description': 'Saccade analysis.',
			},
			'function': ['saccade_em'],
			'input': [name_root + '/'],
			'input_timestamp': [], # virgin
			'output': [], # virgin
		})

		# Data entry, leaf entry
		db.nodes.insert_one({
			'name': name_root + '/',
			'timestamp': int(unix_timestamp()),
			'format': 'gazelle/v1/gaze/simple/',
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
					'target': {'range': [rel_start, -1]},
					'saccade_window': {'range': [rel_start, rel_end]},
				},
			},
			'function': [],
			'input': [],
			'input_timestamp': [],
			'output': norm_g,
		})
