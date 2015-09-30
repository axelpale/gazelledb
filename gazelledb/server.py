
from flask import Flask, jsonify, abort, render_template
app = Flask(__name__)

from pymongo import MongoClient
mongo = MongoClient()
db = mongo.gazelle

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
		# Remove internal data
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
