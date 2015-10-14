'''
Here we use two different concepts, times and indices:
  Time t  0 1 2 3 4 5
          | | | | | |
  Vector [ 2 3 1 2 1 ]
           | | | | |
  Index i  0 1 2 3 4
'''

def select_points_before_time(X, t):
    # Return points before given time index
    return select_first_points(X, t)

def select_points_after_time(X, t):
    # Return columns after given time index.
    return X[t:] # Python handles out of range cases by returning []

def select_first_points(X, n):
    # Return first max n points of X.
    return X[:n]

def select_last_points(X, n):
    # Return last max n points of X
    if n > 0:
        return X[-n:]
    else:
        return []

def select_points_time_to_time(X, t1, t2):
    # Return points according to the time interpretation of indices.
    # Precondition: t1 <= t2 and t1,t2 >= 0.
    return X[t1:t2] # Element at index t2 is excluded

def mean_point(X):
    # Calculate mean of the points
    sum_x = 0
    sum_y = 0
    for p in X:
        sum_x += p[0]
        sum_y += p[1]
    n = len(X)
    return [float(sum_x) / n, float(sum_y) / n]

def weighted_mean_point(X, W):
    # Precondition: sum(W) = 1
    sum_x = 0.0
    sum_y = 0.0
    for p, w in zip(X, W):
        sum_x += w * p[0]
        sum_y += w * p[1]
    return [sum_x, sum_y]
