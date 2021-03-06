
class InterpolationError(Exception):
	pass

def interpolate_using_previous(dictlist, keys):
	'''
	Throw
		InterpolationError
			if a key has no non-null values
	'''
	dl = dictlist # alias
	ndl = [] # new, interpolated dictlist

	if len(dl) < 1:
		raise InterpolationError('Empty list cannot be interpolated')

	first_nonnull = {}

	# Find first non-nulls
	for k in keys:
		for d in dl:
			if d[k] is not None:
				first_nonnull[k] = d[k]
				break

	if len(first_nonnull.keys()) != len(keys):
		# No good values found for every key
		raise InterpolationError('No non-null values to interpolate against: ' + str(first_nonnull))

	prev_nonnull = first_nonnull

	for d in dl:
		nd = d.copy()
		for k in keys:
			if nd[k] is None:
				nd[k] = prev_nonnull[k]
			else:
				prev_nonnull[k] = nd[k]
		ndl.append(nd)

	return ndl
