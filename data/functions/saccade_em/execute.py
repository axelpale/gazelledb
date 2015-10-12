from preprocess import select_and_interpolate_for_em
from math import floor
from em import saccade_model_em

def execute(input_nodes):
	trial = input_nodes[0]
	w, src_xy, tgt_xy = select_and_interpolate_for_em(trial)

	rt, dur, mu_src, mu_tgt, mse, em_iters, src_sse, sacc_sse, tgt_sse, did_converge = saccade_model_em(w, src_xy, tgt_xy)
	# For absolute time: t0 = w[0].time_mics
	srt = floor(rt * 1000 / 300);
	sd = floor(dur * 1000 / 300);

	return {
		'trial_configuration_id': trial['meta']['trial_configuration_id'],
		't_start': rt, 't_end': rt + dur,
		'mse': floor(mse * 10000)/10000.0, 'srt': srt, 'sd': sd,
		'em_iterations': em_iters, 'did_converge': did_converge,
		'source_error': src_sse, 'saccade_error': sacc_sse, 'target_error': tgt_sse,
	}
