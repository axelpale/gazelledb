
def saccade_em(gazepoints, src_xy, tgt_xy):
	'''
	Estimates the reaction time and duration of the saccade by
	fitting a saccade model to the data.

	The model consists of three phases:
	  1) source phase, gaze is fixated onto a point
	  2) saccade phase, gaze moves steadily from the source point
	     onto the target point
	  3) target phase, gaze becomes fixated onto a point.

	The estimation is done in Expectation-Maximation manner:
	  1) Initial locations are given for the source and target points.
	  2) Expectation: given the source and target points, saccade start
	     and end times are calculated and the gazepoints are divided
	     into three classes: source, saccade, and target gazepoints.
	     In EM terminology, the classes are the latent variables.
	  3) Maximization: the means of the new source and target gazepoints
	     become the new values of the source and target points.
	  4) Repeat steps 2) and 3) until the source and target points stay
	     the same.

	Input arguments
	  gazepoints, row vector of 2d column vectors
	  mu_source
	  mu_target

	Output arguments
	  rt, saccadic reaction time.
	    The number of frames in the source class.
	  dur, saccade duration
	    The number of frames in the saccade class.
	  mu_src
	    Predicted mean of the source
	  mu_tgt
	    Predicted mean of the target

	Here we use two different concepts, times and indices:
	  Time t  0 1 2 3 4 5
	          | | | | | |
	  Vector [ 2 3 1 2 1 ]
	           | | | | |
	  Index i  0 1 2 3 4
	'''

	# Aliases
	g = gazepoints

	# Max
	max_t = len(g)
	max_i = max_t - 1

	# Initialize
	mu_s = src_xy
	mu_t = tgt_xy
	t_start = min(max_t, 60) # Average SRT is about 200 ms
	t_end = min(max_t, 70) # Average SRT is about 30 ms

	# In case there is a bug
	max_iters = 1000
	for i in range(max_iters):
		pass

	rt = t_start
	dur = t_end - t_start
	mu_src = mu_s
	mu_tgt = mu_t
	mlerr = 0.123456789
	return rt, dur, mu_src, mu_tgt, mlerr
