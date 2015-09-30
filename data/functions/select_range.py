
def execute(input_series, start=0, end=None):
	'''
	Parameters
	  start
	    int; Python-style indexing: 0 is the first, inclusive
	  end
	    int; Python-style indexing: n is the last, exclusive
	'''
	if end is None:
		end = len(input_series)
	return input_series[start:end]
