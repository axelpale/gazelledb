
from flask import Flask, jsonify, request, abort, render_template
app = Flask(__name__)

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError

# Database connection setup.
# Defaults
#    serverSelectionTimeoutMS=30000
mongo = MongoClient(serverSelectionTimeoutMS=5000)
db = mongo.gazelle

import json
from bson import json_util

from lib import get_node
from lib import create_node

def db_connection_failure(abort_fn, e):
    print 'Connection to database could not be established: ' + e.message
    abort_fn(500)
    return

@app.route('/')
def front():
    try:
        cursor = db.nodes.find(projection=['name']).limit(20)
        node_names = [x['name'] for x in cursor]
        return render_template('index.html', node_names=node_names)
    except ServerSelectionTimeoutError as e:
        return db_connection_failure(abort, e)

@app.route('/test/saccadeem/')
def tester():
    # Compare
    matlab_results = {
        'icl/cg/person/0001/age/8mo/method/8/srt1/trial/02/': {
            't_start': 137, 't_end': 156,
            'mse': 0.0017, 'srt': 456, 'sd': 63,
            'em_iterations': 5,
            'source_error': 0.0369,
            'saccade_error': 0.0183,
            'target_error': 0.4728,
        },
        'icl/cg/person/0001/age/8mo/method/8/srt1/trial/04/': {
            't_start': 78, 't_end': 92,
            'mse': 0.0070, 'srt': 260, 'sd': 46,
            'em_iterations': 4,
            'source_error': 0.0279,
            'saccade_error': 0.0153,
            'target_error': 2.0708,
        },
        'icl/cg/person/0001/age/8mo/method/8/srt2/trial/07/': {
            't_start': 115, 't_end': 130,
            'mse': 0.0023, 'srt': 383, 'sd': 50,
            'em_iterations': 3,
            'source_error': 0.0622,
            'saccade_error': 0.0191,
            'target_error': 0.6249,

        },
        'icl/cg/person/0001/age/8mo/method/8/srt4/trial/09/': {
            't_start': 95, 't_end': 109,
            'mse': 0.0024, 'srt': 316, 'sd': 46,
            'em_iterations': 3,
            'source_error': 0.3362,
            'saccade_error': 0.0441,
            'target_error': 0.3500,
        },
        'icl/cg/person/0002/age/8mo/method/8/srt1/trial/00/': {
            't_start': 96, 't_end': 130,
            'mse': 0.0223, 'srt': 320, 'sd': 113,
            'em_iterations': 3,
            'source_error': 3.3583,
            'saccade_error': 0.1351,
            'target_error': 3.2047,
        },
        'icl/cg/person/0002/age/8mo/method/8/srt1/trial/05/': {
            't_start': 15, 't_end': 137,
            'mse': 0.0359, 'srt': 50, 'sd': 406,
            'em_iterations': 4,
            'source_error': 0.0000,
            'saccade_error': 10.1766,
            'target_error': 0.5995,
        },
    }

    diffs = {}

    for n, o in matlab_results.iteritems():
        n = n + 'saccade/'
        try:
            node = get_node.by_name_computed(db, n)
        except ServerSelectionTimeoutError as e:
            return db_connection_failure(abort, e)
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
    print 'HTTP GET ' + node_name
    try:
        r = get_node.by_name_computed(db, node_name, policy='init')
    except ServerSelectionTimeoutError as e:
        return db_connection_failure(abort, e)
    except:
        import traceback
        traceback.print_exc()
        abort(500)
        return
    if r is None:
        abort(404)
    else:
        # Remove internal data from response
        r.pop('_id', None)
        return json_util.dumps(r)

@app.route('/<path:node_name>', methods=['PUT'])
def insert_node(node_name):
    print 'HTTP PUT ' + node_name

    # Note: aborts with 400 if malformed JSON
    j = request.get_json()

    if 'name' in j:
        if node_name != j['name']:
            abort(400)

    try:
        new_node = create_node.by_prototype(j)
        db.nodes.insert_one(new_node)
    except ServerSelectionTimeoutError as e:
        return db_connection_failure(abort, e)
    except DuplicateKeyError:
        return 'Name already taken: ' + node_name, 400
    except create_node.InvalidNodeCandidate as e:
        return str(e), 400
    except:
        import traceback
        traceback.print_exc()
        abort(500)

    return json_util.dumps(new_node), 200

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
