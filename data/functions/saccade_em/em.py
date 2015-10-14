from mle import saccade_model_mle
from utils import *

def saccade_model_em(gazepoints, src_xy, tgt_xy):
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

    # To detect nonconvergent situations, memorize the visited t_start and
    # t_end pairs and their model error.
    t_history = TimePairValueHistory()

    # Limit iterations in case there is a bug
    max_iters = 50
    em_iters = 0
    for _ in range(max_iters):
        t_start_hat, t_end_hat, mse, src_sse, sacc_sse, tgt_sse = saccade_model_mle(g, mu_s, mu_t, t_start, t_end)

        if t_end_hat < t_start_hat:
            raise Exception('t_end_hat < t_start_hat: ' + str(t_end_hat) + ',' + str(t_start_hat))

        # Determine new centroids.
        # Limit times so that there is at least one gazepoint.
        t_start_c = min(max(t_start_hat, 1), max_t - 1)
        t_end_c   = min(max(t_end_hat  , 1), max_t - 1)
        # Compute means based on windows of 100 ms before and after saccade
        g_source = select_points_time_to_time(g, 0, t_start_c)
        g_target = select_points_time_to_time(g, t_end_c, max_t)
        g_source30 = select_last_points(g_source, 30)
        g_target30 = select_first_points(g_target, 30)
        mu_s_hat = mean_point(g_source30)
        mu_t_hat = mean_point(g_target30)

        mu_s = mu_s_hat
        mu_t = mu_t_hat
        t_start = t_start_hat
        t_end = t_end_hat

        # Compute until we have arrived to same state again.
        if not t_history.is_visited(t_start_hat, t_end_hat):
            t_history.visit(t_start, t_end, mse, {
                'src_sse': src_sse,
                'sacc_sse': sacc_sse,
                'tgt_sse': tgt_sse,
            })
            # The next round either is minimal again or goes here.
            em_iters += 1

            print 't_start: ' + str(t_start)
            print 't_end: ' + str(t_end)
            print 'mse: ' + str(mse)
        else:
            # Select the parameters that gave minimum error
            t_start, t_end, mse, d = t_history.get_minimum()
            src_sse = d['src_sse']
            sacc_sse = d['sacc_sse']
            tgt_sse = d['tgt_sse']
            break

    if em_iters == max_iters:
        did_converge = False
    else:
        did_converge = True

    rt = t_start
    dur = t_end - t_start
    mu_src = mu_s
    mu_tgt = mu_t
    return rt, dur, mu_src, mu_tgt, mse, em_iters, src_sse, sacc_sse, tgt_sse, did_converge
