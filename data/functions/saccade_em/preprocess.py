from interpolate import interpolate_using_previous

def select_and_interpolate_for_em(trial_node):
	'''
	Parameter
	  trial_node
	    list of dicts
	Return
	  list of lists
	'''
	keys = ['gaze_x', 'gaze_y']
	interpolated = interpolate_using_previous(trial_node['output'], keys)

	sw_range = trial_node['meta']['tags']['saccade_window']['range']
	saccade_window = interpolated[sw_range[0]:sw_range[1]]
	src_xy = [0.5, 0.5]
	tgt_xy = [trial_node['meta']['aoi_x_rel'],
	          trial_node['meta']['aoi_y_rel']]

	# Convert to list of lists
	w = [ [d['gaze_x'], d['gaze_y']] for d in saccade_window ]
	return w, src_xy, tgt_xy
