import numpy as np

def distortHorizShear(x, y, alpha):  
    x2 = x + y * np.tan(alpha)
    y2 = y
    return x2, y2

def distortVertShear(x, y, alpha):
    y2, x2 = distortHorizShear(y, x, alpha) 
    return x2, y2

def distortRotate(x, y, beta):
    x2 = x*np.cos(beta) - y*np.sin(beta)
    y2 = x*np.sin(beta) + y*np.cos(beta)
    return x2, y2

def distortScale(x, y, k):
    return k*x, k*y

def warp_distortion_coeffs(src, dst):
    xs = src[:, 0]
    ys = src[:, 1]
    xd = dst[:, 0]
    yd = dst[:, 1]
    rows = src.shape[0]
    
    A = np.zeros((rows * 2, 9))
    
    A[:rows, 0] = xs
    A[:rows, 1] = ys
    A[:rows, 2] = 1
    A[:rows, 6] = - xd * xs
    A[:rows, 7] = - xd * ys
    A[:rows, 8] = xd
    
    A[rows:, 3] = xs
    A[rows:, 4] = ys
    A[rows:, 5] = 1
    A[rows:, 6] = - yd * xs
    A[rows:, 7] = - yd * ys
    A[rows:, 8] = yd
    
    #A = A[:, list(range(9))]
    
    _, _, V = np.linalg.svd(A)
    
    coeffs = - V[-1] / V[-1, -1]
    
    return coeffs

def warp_transformation(coeffs, x, y):
    a_0 = coeffs[0]
    a_1 = coeffs[1]
    a_2 = coeffs[2]
    b_0 = coeffs[3]
    b_1 = coeffs[4]
    b_2 = coeffs[5]
    c_0 = coeffs[6]
    c_1 = coeffs[7]
    
    denominator = c_0 * x + c_1 * y + 1
    
    numerator_x = a_0 * x + a_1 * y + a_2
    
    numerator_y = b_0 * x + b_1 * y + b_2
    
    new_x = numerator_x / denominator
    new_y = numerator_y / denominator
    
    return new_x, new_y    