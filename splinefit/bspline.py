import numpy as np


def cubic(t):
    """
    Evaluate C^2 continuous cubic BSpline basis for each function B0, B1, B2, B3.

    out = [t^3, t^2, t, 1] * B

    To compute the Bspline curve, simply dot the resulting values with the
    control points.

    C(u) = [t^3, t^2, t, 1] * B_i * P, P = [P_i, P_{i+1}, P_{i+2}, P_{i+3}],

    where P are the control points.

    Arguments:
        t : Parameter, `0 <= t <= 1`.

    Returns
        out : Value of Bspline basis in each cell.


    """
    B = np.array([[-1, 3, -3, 1],
                 [3, -6, 3, 0],
                 [-3, 0, 3, 0],
                 [1, 4, 1, 0]])/6
    u = np.array([t**3, t**2, t, 1])

    out = u.dot(B)
    return out


def normalize(pts, n):
    """
    Renormalize points so that for each point `pt`, we have `0 <= pt <= n`.

    Arguments:
        pts : List of points (array of size (m,))
        n : Number of control points - 1.

    Returns:
        out : Normalized points
        nc : Normalization constants

    """
    pmin = np.min(pts) 
    pmax = np.max(pts)
    out = n*(pts - pmin)/(pmax - pmin)
    nc = (pmin, pmax)
    return out, nc 


def denormalize(npts, nc, n):
    """
    Restore normalized points, to their original, unnormalized representation

    Arguments:
        npts : List of normalized points (array of size (m,))
        nc : Normalization constants (see `normalize`)
        n : Number of control points - 1.

    Returns:
        out : Normalized points

    """
    out = npts*(nc[1] - nc[0])/n + nc[0]
    return out

def lower(pts):
    """
    Determine the lowest index of the control points that lie in the
    neighborhood of the query points `pts`.

    Arguments:
        pts : Query points, must be normalized to 0 <= pts <= n, where n+1 is
            the number of control points.
    """
    return int(np.floor(pts) - 1)

def upper(pts):
    """
    Same as `lower`, but returns the highest index.
    """
    return int(np.floor(pts) + 2)

def min_degree(num_pts, p):
    """
    Determines the minimum degree that can be used to fit a set of points.

    Args:
        num_pts : Number of points
        p : Desired polynomial degree

    If degree p can be used to fit the points, this function returns p.
    Otherwise, it returns the minimum degree that can used to fit the set of
    points.

    """
    return min(p, max(num_pts - p, 1))


def eval(P, npts=10):

    t = np.linspace(0, 1, npts)
    x = np.zeros(((len(P)-3)*npts,))
    y = np.zeros(((len(P)-3)*npts,))
    k = 0
    for i in range(1,len(P)-2):
        ctrlpts = P[i-1:i+3]
        for ti in t:
            qx = cubic(ti).dot(ctrlpts)
            y[k] = qx
            x[k] = i + ti - 1
            k += 1
    return x, y


def eval_basis(xc, n):
    idx = np.floor(xc)
    t = (xc - idx)/n
    w = cubic(t)
    return w


def set_ctrlpt(xc, yc, n):
    """

    Assign value to control point by solving the constrained optimization
    problem:

    min || \sum_a P_a ||^2 subject to \sum_a w_a P_a = yc

    Solution is given by:

    P_k = w_k*yc/(sum_a w_a^2)

    Arguments:
        xc : x-coordinate of point. Determines which control point to
            influence. 
        yc : y-coordinate of point. Determines what weight to assign to the
            affected control point.
         n : Number of control points - 1

    Returns:
        val : Value of control point.
        idx : Index of control point.

    """

    w = eval_basis(xc, n)
    return w*yc/(w.dot(w)), (lower(xc) + 2, upper(xc) + 3) 


def findspan(n, p, u, U):
    """

    n : Number of control points
    p : degree
    u : parameter to find span for, should lie in 0 <= u <= 1.
    U : knot vector

    """
    if u == U[n+1]:
        return n

    for i in range(p, p + n):
        if u >= U[i] and u < U[i+1]:
            return i
    return n
    low = p
    high = n + 1
    mid = int((low+high)/2)
    while (u < U[mid] or u >= U[mid+1]):
        if (u < U[mid]):
            high = mid
        else:
            low = mid
        mid = int((low + high)/2)
    return mid


def basisfuns(i,u,p,U):
    N = np.zeros((p+1,))
    left = np.zeros((p+1,))
    right = np.zeros((p+1,))
    N[0] = 1.0


    if np.isclose(u, U[0]):
        return [1.0] + [0]*p
    if np.isclose(u, U[-1]):
        return [0]*p + [1.0]

    for j in range(1,p+1):
        left[j] = u - U[i+1-j]
        right[j] = U[i+j] - u
        saved = 0.0
        for r in range(j):
            denom = right[r+1] + left[j-r]
            if np.isclose(denom,0):
                N[r] = 0
                break
            temp = N[r]/denom
            N[r] = saved+right[r+1]*temp
            saved = left[j-r]*temp
        N[j] = saved

    return N


def curvepoint(p, U, P, u):
    C = 0.0
    n = len(P) - p
    span = findspan(n, p, u, U)
    N = basisfuns(span,u,p,U)
    if U[-1] == u:
        return P[-1]
    for i in range(p+1):
        C = C + N[i]*P[span-p+i]
    return C


def surfacepoint(pu, pv, U, V, P, u, v):
    S = 0.0

    nv = P.shape[0] - 1
    nu = P.shape[1] - 1
    span_u = findspan(nu, pu, u, U)
    span_v = findspan(nv, pv, v, V)
    Nu = basisfuns(span_u,u,pu,U)
    Nv = basisfuns(span_v,v,pv,V)

    for i in range(pu+1):
        for j in range(pv+1):
            P[span_v-pv+j,0]
            P[0, span_u-pu+i]
            S = S + Nu[i]*Nv[j]*P[span_v-pv+j, span_u-pu+i]
    return S


def evalcurve(p, U, P, u):
    y = 0*u
    for i in range(len(u)):
        y[i] = curvepoint(p, U, P, u[i])
    return y


def dist2curve(p, U, Px, Py, Pz, u, x, y, z):
    cx = evalcurve(p, U, Px, u)
    cy = evalcurve(p, U, Py, u)
    cz = evalcurve(p, U, Pz, u)
    dists = np.sqrt((cx - x)**2 + (cy - y)**2 + (cz - z)**2)
    return dists


def evalsurface(pu, pv, U, V, P, u, v):
    w = np.zeros((len(u), len(v)))
    for i in range(w.shape[0]):
        for j in range(w.shape[1]):
            w[i,j] = surfacepoint(pu, pv, U, V, P, u[i], v[j])
    return w


def uvinv(xp, yp, u0, v0, l, r, b, t):
    """
    Invert transfinite interpolation mapping. That is, given (x,y) determine
    (u,v). Secant method is used to find the root. 
    Nearest index in rectangular grid can be used as initial guess.

    """
    import scipy.optimize 

    xb0 = curvepoint(b.p, b.U, b.Px, 0)
    xb1 = curvepoint(b.p, b.U, b.Px, 1)

    xt0 = curvepoint(t.p, t.U, t.Px, 0)
    xt1 = curvepoint(t.p, t.U, t.Px, 1)

    yl0 = curvepoint(l.p, l.U, l.Py, 0)
    yl1 = curvepoint(l.p, l.U, l.Py, 1)
    
    yr0 = curvepoint(r.p, r.U, r.Py, 0)
    yr1 = curvepoint(r.p, r.U, r.Py, 1)

    def swap(a, b, curve):
        if a < b:
            tmp = a
            a = b
            b = tmp
            curve.Px = curve.Px[::-1]
            curve.Py = curve.Py[::-1]

        return a, b, curve

    xt1, xt0, t = swap(xt1, xt0, t)
    xb1, xb0, b = swap(xb1, xb0, b)
    yl1, yl0, l = swap(yl1, yl0, l)
    yr1, yr0, r = swap(yr1, yr0, r)

    x = lambda u,v :  (1 - u)*curvepoint(l.p, l.U, l.Px, v) \
             + u*curvepoint(r.p, r.U, r.Px, v)\
             + (1 - v)*curvepoint(b.p, b.U, b.Px, u) \
             + v*curvepoint(t.p, t.U, t.Px, u) \
        - (1 - u)*(1 - v)*xb0 - (1 - u)*v*xt0 - u*(1 - v)*xb1 -u*v*xt1 \
        - xp
    y = lambda u,v : (1 - u)*curvepoint(l.p, l.U, l.Py, v) \
             + u*curvepoint(r.p, r.U, r.Py, v)\
             + (1 - v)*curvepoint(b.p, b.U, b.Py, u) \
             + v*curvepoint(t.p, t.U, t.Py, u) \
        - (1 - u)*(1 - v)*yl0 - (1 - u)*v*yl1 - u*(1 - v)*yr0 -u*v*yr1 \
        - yp

    f = lambda u : (x(u[0], u[1]), y(u[0], u[1]))
 
    x0 = [u0, v0]
    root = scipy.optimize.root(f, x0, args=(), method='broyden1', tol=1e-2,
            options={'maxiter' : 30}) 

    # Force solution to lie in the uv grid
    def clamp(x):
        if x < 0:
            return 0
        if x > 1:
            return 1
        else:
            return x

    x = root.x
    x[0] = clamp(x[0])
    x[1] = clamp(x[1])
    return x


def uniformknots(m, p, a=0, b=1):
    """
    Construct a uniform knot vector

    Arguments:
    m : Number of interior knots
    p : Polynomial degree
    a(optional) : left boundary knot
    b(optional) : right boundary knot

    """
    t = np.linspace(a,b,m+2)
    U = np.r_[(a,)*(p+1),
              t[1:-1],
              (b,)*(p+1)]
    return U

def numknots(n, p,  interior=0):
    """
    Determine the number of knots given control points

    Arguments:
      n : Number of control points
      p : Polynomial degree
    """
    m = n + p + 1  
    if interior == 0:
        return m
    else:
        return m - 2*(p + 1)


def customknots(t, p, a=0, b=1):
    U = np.r_[(a,)*(p+1),
              t,
              (b,)*(p+1)]
    return U



def kmeansknots(s, m, p, a=0, b=1.0):
    """
    Construct a knot vector by finding knot positions using kmeans for selecting
    knots.
    """
    t = np.linspace(a,b,m)
    from scipy.cluster.vq import vq, kmeans
    t = np.sort(kmeans(s, m)[0])
    U = np.r_[(a,)*(p+1),
              t,
              (b,)*(p+1)]
    return U

def averageknots(s, m, p, a=0.0, b=1.0):
    """
    Construct a knot vector by finding knot positions using averaging for selecting
    knots.
    """
    t = np.zeros((m+2,))
    for i in range(m+2):
        t[i] = sum(s[i:i+p-1])*1.0/p
    U = np.r_[(a,)*(p+1),
              t,
              (b,)*(p+1)]
    return U


def svd_inv(A, b, s, tol=1e-8, D=0):
    """
    Solve Ax = b using least squares SVD and regularization. 

    That is solve the regularized Normal equations: 
    (A.T*A + s*I + D)*x = A.T*b

    """
    M = A.T.dot(A) + s*np.eye(A.shape[1]) + D
    uh, sh, vh = np.linalg.svd(M, full_matrices=False)
    m = sh.shape[0]
    shi = 0*np.zeros((m,))
    for i in range(m):
        if sh[i] > tol:
            shi[i] = 1/sh[i]
        else:
            shi[i] = 0
            
    v = A.T.dot(b)
    Mi = (vh.T*shi).dot(uh.T)
    return Mi.dot(A.T.dot(b) )


def lsq(x, y, U, p, s=0, tol=1e-6, a=0, w=0):
    """
    Computes the least square fit to the data (x,y) using the knot vector U.

    Arguments:
        x, y : Data points
        U : Knot vector
        p : Degree of BSpline
        s : Smoothing parameter
        a : Jump penalty regularization
        w : Weights

    Returns:
        P : Control points,
        res : residuals

    """
    assert len(x) == len(y)
    m = len(U) - 1
    n = m - p - 1
    npts = len(x)

    A = np.zeros((npts, m - p))
    b = np.zeros((npts,))
    if np.all(w) == 0:
        w = np.zeros((m-p,))
    for i, xi in enumerate(x):
        span = findspan(n, p, xi, U)
        N = basisfuns(span, xi, p, U)
        for j, Nj in enumerate(N):
            A[i, span + j - p] = Nj
        b[i] = y[i] 

    # Jump regularization
    D = derivative_matrix(m - p)
    R = a*D.T.dot(np.diag(w)).dot(D)

    p0 = svd_inv(A, b, s, tol, D=R) 
    res = np.linalg.norm(A.dot(p0) - b)
    # Interpolate ends
    p0[0] = y[0] 
    p0[-1] = y[-1] 
    return p0, res


def derivative_matrix(n):
    """
    Second derivative approximated by finite differences. 

    """
    if n == 2:
        D = np.zeros((2, 2))
        D[0,0] = -1
        D[0,1] = 1
        D[1,0] = -1
        D[1,1] = 1
        return D


    D = np.zeros((n, n))
    D[0,0] = 1
    D[0,1] = -2
    D[0,2] = 1
    for i in range(1, n-1):
        D[i, i + 1] = 1
        D[i, i - 0] = -2
        D[i, i - 1] = 1
    D[-1,0] = 1
    D[-1,1] = -2
    D[-1,2] = 1
    return D


def lsq2surf(u, v, z, U, V, pu, pv, corner_ids=0, tol=1e-12, s=0.2, a=0.1):
    """
    Computes the least square fit to the mapped data z(u, v) using the knot
    vector U, V.

    Arguments:
        u, v : Mapping of (x, y) coordinates of data points to parameterization
        z : Coordinate to apply fit to.
        U, V : Knot vector
        pu, pv : Degree of BSpline in each direction

    Optional arguments:
        corner_ids : Specify a list of four index to force the corners to be
            interpolated. Each id must map to an value in `u, v, z`.

    Returns:
        P : Control points (size: mu x mv),
        res : residuals

    """
    assert len(u) == len(v)
    assert len(u) == len(z)

    mu = len(U) - 1
    mv = len(V) - 1
    nu = mu - pu - 1
    nv = mv - pv - 1
    npts = len(z)

    A = np.zeros((npts, (nu + 1)*(nv + 1)))
    b = np.zeros((npts,))
    for i in range(npts):
        ui = u[i]
        vi = v[i]
        zi = z[i]
        span_u = findspan(nu, pu, ui, U)
        span_v = findspan(nv, pv, vi, V)
        Nu = basisfuns(span_u, ui, pu, U)
        Nv = basisfuns(span_v, vi, pv, V)
        for k, Nk in enumerate(Nu):
            for l, Nl in enumerate(Nv):
                A[i, (span_v + l - pv)*(mu - pu) + (span_u + k - pu)] = Nk*Nl
        b[i] = zi

    su = (nu + 1)
    sv = (nv + 1)
    D = np.zeros((su * sv, su *sv))
    for i in range(1, su-1):
        for j in range(sv):
            D[i + j * su, i - 1 + j * su] += 1.0 
            D[i + j * su, i + j * su] += - 2.0
            D[i + j * su, i + 1 + j * su] += 1.0

    for i in range(su):
        for j in range(1, sv-1):
            D[i + j * su, i + j * su] += - 2.0
            D[i + j * su, i + (j - 1) * su] += 1.0
            D[i + j * su, i + (j + 1) * su] += 1.0

    h = 1.0 / (nu - 1)
    R = a*D.T.dot(D) / h**2

    p0 = svd_inv(A, b, s, tol, D=R) 

    res = np.linalg.norm(A.dot(p0) - b)
    P = p0.reshape((mv-pv, mu-pu))

    return P, res

def chords(x, y, z=None, a=0, b=1):
    """
    Map (x_j, y_j, z_j) to the interval a <= s_j <=b using the chord length
    parameterization.

    s_0 = a 
    s_1 = a + d_1, 
    s_j = s_{j-1} + d_j
    where d_j = dist(P_j - P_{j-1}), and P_j = (x_j, y_j).

    """
    dx = x[1:] - x[0:-1]
    dy = y[1:] - y[0:-1]
    if z is None:
        dz = 0
    else:
        dz = z[1:] - z[0:-1]

    dists = np.sqrt(dx**2 + dy**2 + dz**2)
    d = np.zeros((len(dists)+1,))
    for i in range(len(dists)):
        d[i+1] = d[i] + dists[i]

    d = (b-a)*(d-min(d))/(max(d)-min(d)) + a
    return d

def centripetal(x, y, a=0, b=1):
    """
    Map (x_j, y_j) to the interval a <= s_j <=b using the centripetal 
    parameterization.

    See page 365 in Nurbs Book

    """
    dx = x[1:] - x[0:-1]
    dy = y[1:] - y[0:-1]
    dists = np.sqrt(dx**2 + dy**2)
    dl = sum(np.sqrt(dists))
    d = np.zeros((len(x),))
    for i in range(len(dists)):
        d[i+1] = d[i] + np.sqrt(dists[i])/dl
    #d = (b-a)*(d-min(d))/(max(d)-min(d)) + a
    d = (b-a)*d + a
    return d


def xmap(x, a=0, b=1):
    """
    Map real number x to the interval a <= s_j <=b by normalizing values.

    """

    denom = max(x)-min(x)
    if np.isclose(denom,0):
        denom = 1
    d = (x-min(x))/denom
    d = (b-a)*d + a
    
    return d


def argsort2(u, v):
    """
    Sort the two arrays `u` and `v` treating them as separate dimensions. 
    The order of the output is 
    `w[0] = i[0] + nu*j[0]`
    `w[1] = i[1] + nu*j[0]`
    where `i[0]` is `argmin(u)` and `j[0]` is `argmin(v)`. Hence, `i[1]` is the
    index of the second smallest value in `u` and so forth.
    """
    assert len(u) == len(v)
    i = np.argsort(u)
    j = np.argsort(v)
    w = np.zeros((len(u),))


def lsq2(s, x, y, U, p, smooth=0):
    """
    Fit a curve C(s) = sum_i B_i(s) P, where control points P = (P_x, P_y)

    s defines the mapping of each data point (x_j, y_j) to the curve parameter
    s_j. A simple mapping to use is the L2 distance between points `see l2map`.

    Arguments:
        s : Mapping of (x,y) to the curve
        U : Knot vector
        p : Polynomial degree.

    Returns:
        Px, Py : The coordinates of the control points.
        res : Residuals.

    """
    Px, rx = lsq(s, x, U, p, s=smooth)
    Py, ry = lsq(s, y, U, p, s=smooth)
    return Px, Py, (rx, ry)


def smoothing(x, y, sm=0.1, mmax=100, disp=False, p=3):
    """
    Perform least squares fitting by successively increasing the number of knots
    until a desired residual threshold is reached.

    Returns:
        Px, Py : Control points
        U : Knot vector

    """

    m = 2
    it = 0
    res = sm + 1
    while (res > sm and m < mmax):
        it += 1
        Px, Py, U, res = lsq2l2(x, y, m, p)
        res = np.linalg.norm(res)
        if disp:
            print("Iteration: %d, number of knots: %d, residual: %g" % (it, m,
                res))
        m = 2+m
    return Px, Py, U


def lsq2l2(x, y, m, p, knots='uniform', smooth=0):
    """
    Perform least squares fitting using `m` number of knots and chordlength
    parameterization and averaged knot vector.
    """
    s = chords(x, y, a=0, b=1)
    #s = np.linspace(0, 1, len(x))
    if knots == 'uniform':
        U = uniformknots(m, p, a=0, b=1)
    elif knots == 'kmeans':
        U = kmeansknots(s, m, p, a=0, b=1)
    Px, Py, res = lsq2(s, x, y, U, p, smooth=smooth)
    return Px, Py, U, res


def lsq2x(x, y, m, p, axis=0):
    """
    Perform least squares fitting using `m` number of knots and normalization of
    input coordinates to 0 <= s <= 1. Argument `axis` controls which coordinate
    to use in the mapping process.
    """
    if axis == 0:
        s = xmap(x, m, a=0, b=1)
    else:
        s = xmap(y, m, a=0, b=1)

    U = uniformknots(m, p, a=0, b=1)
    Px, Py, res = lsq2(s, x, y, U, p)
    return Px, Py, U, res


class Curve(object):

    def __init__(self, U, p, Px, Py, Pz, label='untitled'):
        """
        Initialize BSpline curve

        Args:
          U : knot vector
          p : degree
          Px : Control points in x-direction
          Py : Control points in y-direction
          Pz : Control points in z-direction

        number of control points: n
        number of knots : m

        Number of knots: m = n + p + 1

        """
        assert len(U) == p + len(Px) + 1
        self.U = U
        self.p = int(p)
        self.Px = Px
        self.Py = Py
        self.Pz = Pz
        self.rwPx = Px
        self.rwPy = Py
        self.rwPz = Pz
        self.label = label

    def eval(self, npts=10, rw=0):
        u = np.linspace(self.U[0], self.U[-1], npts)
        x = 0*u
        y = 0*u
        z = 0*u
        for i in range(npts):
            if rw:
                x[i] = curvepoint(self.p, self.U, self.rwPx, u[i])
                y[i] = curvepoint(self.p, self.U, self.rwPy, u[i])
                z[i] = curvepoint(self.p, self.U, self.rwPz, u[i])
            else:
                x[i] = curvepoint(self.p, self.U, self.Px, u[i])
                y[i] = curvepoint(self.p, self.U, self.Py, u[i])
                z[i] = curvepoint(self.p, self.U, self.Pz, u[i])

        return (x, y, z)

    def json(self, filename):
        import json
        with open(filename, 'w') as out:
            json.dump({
                       'Px' : self.Px.tolist(), 
                       'Py' : self.Py.tolist(), 
                       'Pz' : self.Pz.tolist(),
                       'real_world_Px' : self.rwPx.tolist(), 
                       'real_world_Py' : self.rwPy.tolist(), 
                       'real_world_Pz' : self.rwPz.tolist(),
                       'U' : self.U.tolist(), 
                       'p' : self.p},
                       out, indent=4)


    def iges(self, rw=1):
        from splinefit.iges import IGESBSplineCurve
        if rw:
             return IGESBSplineCurve(self.rwPx, self.rwPy, self.rwPz,
                     self.U.tolist(),
                     self.p)
        else:
            return IGESBSplineCurve(self.Px, self.Py, self.Pz, self.U.tolist(),
                    self.p)

    def __str__(self):
        out = []
        out += ["BSpline Curve: %s" % self.label]
        out += ["Control points:    %d" % len(self.Px)]
        out += ["Degree:            %d" % self.p]
        return '\n'.join(out)


class Surface(object):

    def __init__(self, U, V, pu, pv, Px, Py, Pz, label='untitled'):
        """
        U, V : knot vectors in each direction
        pu, pv : Degree in each direction
        Px, Py, Pz : Control points
        """

        assert len(U) == pu + Px.shape[1] + 1
        assert len(V) == pv + Px.shape[0] + 1
        self.U = U
        self.V = V
        self.pu = int(pu)
        self.pv = int(pv)
        self.Px = Px
        self.Py = Py
        self.Pz = Pz
        self.rwPx = Px
        self.rwPy = Py
        self.rwPz = Pz
        self.label = label

    def eval(self, nu=10, nv=10, rw=0):
        u = np.linspace(self.U[0], self.U[-1], nu)
        v = np.linspace(self.V[0], self.V[-1], nv)

        if rw:
            self.X = evalsurface(self.pu, self.pv, self.U, self.V, 
                                 self.rwPx, u, v)
            self.Y = evalsurface(self.pu, self.pv, self.U, self.V, 
                                 self.rwPy, u, v)
            self.Z = evalsurface(self.pu, self.pv, self.U, self.V, 
                                 self.rwPz, u, v)
        else:
            self.X = evalsurface(self.pu, self.pv, self.U, self.V, 
                                 self.Px, u, v)
            self.Y = evalsurface(self.pu, self.pv, self.U, self.V, 
                                 self.Py, u, v)
            self.Z = evalsurface(self.pu, self.pv, self.U, self.V, 
                                 self.Pz, u, v)

    def json(self, filename):
        import json
        with open(filename, 'w') as out:
            json.dump({
                       'Px' : self.Px.tolist(), 
                       'Py' : self.Py.tolist(), 
                       'Pz' : self.Pz.tolist(),
                       'real_world_Px' : self.rwPx.tolist(), 
                       'real_world_Py' : self.rwPy.tolist(), 
                       'real_world_Pz' : self.rwPz.tolist(),
                       'U' : self.U.tolist(), 
                       'V' : self.V.tolist(),
                       'pu' : self.pu,
                       'pv' : self.pv}, out, indent=4)

    def __str__(self):
        out = []
        out += ["BSpline Surface: %s " % self.label]
        out += [" * Control points:  %d x %d " % (self.Px.shape[0],
                self.Px.shape[1])]
        out += [" * Degree:          (%d, %d) " % (self.pu, self.pv)]
        return '\n'.join(out)

    def compute_distances(self, points, ord=2):
        """
        Assign misfit. The misfit is defined as the distance of each point of
        the spline surface to the nearest query points `points`.

        Args:
            points: Points to compute distances to.
            ord: Metric type. Defaults to `L2` (ord=2). Use `order=1` for L1
                distance.
        """
        if not hasattr(self, 'X'):
            raise ValueError("Call eval() before calling this function.")
        distances = self.X*0
        for i in range(self.misfit.shape[0]):
            for j in range(self.misfit.shape[1]):
                p = (self.X[i, j], self.Y[i, j], self.Z[i, j])
                dist = np.linalg.norm(points -
                                      np.tile(p, (points.shape[0], 1)),
                                      axis=1, ord=ord)
                distances[i, j] = np.min(dist)
        return distances

    def compute_misfit(self, u, v, points, ord=2):
        """
        Assign misfit. The misfit is defined as the distance of each point of
        the spline surface to the nearest query points `points`.

        Args:
            u, v : Mapping to surface.
            points: Coordinates in space.
            ord: Metric type. Defaults to `L2` (ord=2). 
                Use `order=1` for L1 distance.

        """
        error = 0*u
        i = 0
        for ui, vi in zip(u, v):
            x = surfacepoint(self.pu, self.pv, self.U, self.V, self.rwPx, 
                             ui, vi)
            y = surfacepoint(self.pu, self.pv, self.U, self.V, self.rwPy, 
                             ui, vi)
            z = surfacepoint(self.pu, self.pv, self.U, self.V, self.rwPz,
                             ui, vi)
            pi = points[i, :]
            distvec = (x - pi[0], y - pi[1], z - pi[2])
            error[i] = np.linalg.norm(distvec, ord=ord)
            i += 1
        return error
        
    def distance(self, u, v, point, ord=2, coordinates="local", surf_point=0):
        """
        Compute the distance between a query point and the surface. The
        parameterization of the query point must be known.

        Args:
            u, v : Mapping to surface.
            points: Coordinates in space.
            ord: Metric type. Defaults to `L2` (ord=2). 
                Use `order=1` for L1 distance.
        """
        if coordinates == "local":
                x = surfacepoint(self.pu, self.pv, self.U, self.V, self.Px, 
                                 u, v)
                y = surfacepoint(self.pu, self.pv, self.U, self.V, self.Py, 
                                 u, v)
                z = surfacepoint(self.pu, self.pv, self.U, self.V, self.Pz,
                                 u, v)
        elif coordinates == "global":
                x = surfacepoint(self.pu, self.pv, self.U, self.V, self.rwPx, 
                                 u, v)
                y = surfacepoint(self.pu, self.pv, self.U, self.V, self.rwPy, 
                                 u, v)
                z = surfacepoint(self.pu, self.pv, self.U, self.V, self.rwPz,
                                 u, v)
        else:
                raise ValueError("Unknown coordinate type: %s" % coordinates)

        if surf_point:
                return (x, y, z)

        distvec = (x - point[0], y - point[1], z - point[2])
        return distvec[0]**2 + distvec[1]**2 + distvec[2]**2

    def surfacepoints(self, u, v, points, ord=2):
        px = 0*u
        py = 0*u
        pz = 0*u
        i = 0
        for ui, vi in zip(u, v):
            x = surfacepoint(self.pu, self.pv, self.U, self.V, self.rwPx, 
                             ui, vi)
            y = surfacepoint(self.pu, self.pv, self.U, self.V, self.rwPy, 
                             ui, vi)
            z = surfacepoint(self.pu, self.pv, self.U, self.V, self.rwPz,
                             ui, vi)
            px[i] = x
            py[i] = y
            pz[i] = z
            i += 1
        return (px, py, pz)

    def iges(self, rw=1):
        """
        Send Bspline surface to IGES data representation

        """
        from splinefit.iges import IGESBSplineSurface
        if rw:
            return IGESBSplineSurface(self.rwPx, self.rwPy, self.rwPz, 
                                 self.U.tolist(), self.V.tolist(), self.pu, self.pv)
        else:
            return IGESBSplineSurface(self.Px, self.Py, self.Pz, 
                                      self.U.tolist(), self.V.tolist(), self.pu, self.pv)
  
