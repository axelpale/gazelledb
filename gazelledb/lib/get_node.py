from compute import compute_node

def by_name(db, node_name):
	'''
	Returns None if not found
	'''
	return db.nodes.find_one({ 'name': node_name })

def by_id(db, node_id):
	'''
	Returns None if not found
	'''
	return db.nodes.find_one({ '_id': node_id })

def by_name_computed(db, node_name):
	'''
	Returns None if not found
	'''
	n = by_name(db, node_name)
	if n is None:
		return n
	return compute_node(db, n)

def by_id_computed(db, node_id):
	'''
	Returns None if not found
	'''
	n = by_id(db, node_id)
	if n is None:
		return n
	return compute_node(db, n)
