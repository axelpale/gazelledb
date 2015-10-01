from interpolate import interpolate_using_previous
from math import floor
from em import saccade_em

def execute(input_nodes):
	trial = input_nodes[0]
	sw_range = trial['meta']['tags']['saccade_window']['range']
	saccade_window = trial['output'][sw_range[0]:sw_range[1]]
	src_xy = [0.5, 0.5]
	tgt_xy = [trial['meta']['aoi_x_rel'],
	          trial['meta']['aoi_y_rel']]

	keys = ['gaze_x', 'gaze_y']
	interpolated_window = interpolate_using_previous(saccade_window, keys)
	# Convert to list of lists
	w = [ [d['gaze_x'], d['gaze_y']] for d in interpolated_window]

	rt, dur, mu_src, mu_tgt, mse = saccade_em(w, src_xy, tgt_xy)
	#t0 = w[0].time_mics
	srt = floor(rt * 1000 / 300);
	sd = floor(dur * 1000 / 300);

	return {
		't_start': rt, 't_end': rt + dur,
		'mse': floor(mse*10000)/10000, 'srt': srt, 'sd': sd,
	}
