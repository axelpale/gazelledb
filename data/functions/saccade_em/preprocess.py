from interpolate import interpolate_using_previous

def select_and_interpolate_for_em(trial_node):
	'''
	Parameter
	  trial_node
	    list of dicts
	Return
	  list of lists
	'''
	sw_range = trial_node['meta']['tags']['saccade_window']['range']
	saccade_window = trial_node['output'][sw_range[0]:sw_range[1]]
	src_xy = [0.5, 0.5]
	tgt_xy = [trial_node['meta']['aoi_x_rel'],
	          trial_node['meta']['aoi_y_rel']]

	keys = ['gaze_x', 'gaze_y']
	interpolated_window = interpolate_using_previous(saccade_window, keys)
	# Convert to list of lists
	w = [ [d['gaze_x'], d['gaze_y']] for d in interpolated_window ]
	return w, src_xy, tgt_xy
