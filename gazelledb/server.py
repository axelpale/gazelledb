
from flask import Flask, jsonify, abort, render_template
app = Flask(__name__)

from pymongo import MongoClient
mongo = MongoClient()
db = mongo.gazelle

import json
from bson import json_util

from lib import get_node

# Enable custom node function import
import sys, os
dup = os.path.dirname
env_root = dup(dup(__file__))
sys.path.append(os.path.join(env_root, 'data'))


@app.route('/')
def front():
	cursor = db.nodes.find(projection=['name']).limit(20)
	node_names = [x['name'] for x in cursor]
	return render_template('index.html', node_names=node_names)

@app.route('/test/saccadeem/')
def tester():
	# Compare
	matlab_results = {
		'icl/cg/person/0001/age/8mo/method/8/srt1/trial/02/': {
			't_start': 137, 't_end': 156,
			'mse': 0.0017, 'srt': 456, 'sd': 63,
		},
		'icl/cg/person/0001/age/8mo/method/8/srt1/trial/04/': {
			't_start': 78, 't_end': 92,
			'mse': 0.0070, 'srt': 260, 'sd': 46,
		},
		'icl/cg/person/0001/age/8mo/method/8/srt2/trial/07/': {
			't_start': 115, 't_end': 130,
			'mse': 0.0023, 'srt': 383, 'sd': 50,
		},
		'icl/cg/person/0001/age/8mo/method/8/srt4/trial/09/': {
			't_start': 95, 't_end': 109,
			'mse': 0.0024, 'srt': 316, 'sd': 46,
		},
		'icl/cg/person/0002/age/8mo/method/8/srt1/trial/00/': {
			't_start': 96, 't_end': 130,
			'mse': 0.0223, 'srt': 320, 'sd': 113,
		},
		'icl/cg/person/0002/age/8mo/method/8/srt1/trial/05/': {
			't_start': 15, 't_end': 137,
			'mse': 0.0359, 'srt': 50, 'sd': 406,
		},
	}

	diffs = {}

	for n, o in matlab_results.iteritems():
		n = n + 'saccade/'
		node = get_node.by_name_computed(db, n)
		if node is None:
			diffs[n] = 'not found'
		else:
			if cmp(node['output'], o) == 0:
				diffs[n] = 'match'
			else:
				diffs[n] = {
					'expected': o,
					'was': node['output']
				}

	return json.dumps(diffs)

@app.route('/<path:node_name>', methods=['GET'])
def node(node_name):
	print 'Request: ' + node_name
	try:
		r = get_node.by_name_computed(db, node_name)
	except:
		import traceback
		traceback.print_exc()
		abort(500)
	if r is None:
		abort(404)
	else:
		# Remove internal data from response
		r.pop('_id', None)
		return json_util.dumps(r)

@app.errorhandler(404)
def page_not_found(error):
	return render_template('error404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
	return render_template('error500.html'), 500

if __name__ == '__main__':
	app.run(debug=True)
