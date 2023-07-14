import time

class fluid:

    def __init__(self, d_width, d_rate, visc, t_space):
        self.d_width = d_width
        self.d_rate = d_rate
        self.visc = visc
        self.t_space = t_space
        self.size = (d_width + 2) ** 2

    def xy_coordinate(self, d_width, i, j):
        n = int(i + j * (d_width + 2))
        if n < self.size:
            n = n
        else:
            n = self.size - 1
        return n

    def add_source(self, x, s, dt):
        for i in xrange(self.size):
            x[i] += dt * s[i]
            
    def set_bounds(self, d_width, b, x):
        for i in xrange(1, d_width + 1):
            if b == 0:
                x[self.xy_coordinate(d_width, 0, i)] = x[
                    self.xy_coordinate(d_width, 1, i)]
                x[self.xy_coordinate(
                    d_width, d_width + 1, i)] = x[self.xy_coordinate(d_width, d_width, i)]
                x[self.xy_coordinate(d_width, i, 0)] = x[
                    self.xy_coordinate(d_width, i, 1)]
                x[self.xy_coordinate(
                    d_width, i, d_width + 1)] = x[self.xy_coordinate(d_width, i, d_width)]
            elif b == 1:
                x[self.xy_coordinate(d_width, 0, i)] = - \
                    x[self.xy_coordinate(d_width, 1, i)]
                x[self.xy_coordinate(
                    d_width, d_width + 1, i)] = -x[self.xy_coordinate(d_width, d_width, i)]
                x[self.xy_coordinate(d_width, i, 0)] = x[
                    self.xy_coordinate(d_width, i, 1)]
                x[self.xy_coordinate(
                    d_width, i, d_width + 1)] = x[self.xy_coordinate(d_width, i, d_width)]
            elif b == 2:
                x[self.xy_coordinate(d_width, 0, i)] = x[
                    self.xy_coordinate(d_width, 1, i)]
                x[self.xy_coordinate(
                    d_width, d_width + 1, i)] = x[self.xy_coordinate(d_width, d_width, i)]
                x[self.xy_coordinate(d_width, i, 0)] = - \
                    x[self.xy_coordinate(d_width, i, 1)]
                x[self.xy_coordinate(
                    d_width, i, d_width + 1)] = -x[self.xy_coordinate(d_width, i, d_width)]

        x[self.xy_coordinate(d_width, 0, 0)] = 0.5 * (x[self.xy_coordinate(d_width, 1, 0)] + x[self.xy_coordinate(d_width, 0, 1)])
        x[self.xy_coordinate(d_width, 0, d_width + 1)] = 0.5 * (x[self.xy_coordinate(d_width, 1, d_width + 1)] + x[self.xy_coordinate(d_width, 0, d_width)])
        x[self.xy_coordinate(d_width, d_width + 1, 0)] = 0.5 * (x[self.xy_coordinate(d_width, d_width, 0)] + x[self.xy_coordinate(d_width, d_width + 1, 1)])
        x[self.xy_coordinate(d_width, d_width + 1, d_width + 1)] = 0.5 * (x[self.xy_coordinate(d_width, d_width, d_width + 1)] + x[self.xy_coordinate(d_width, d_width + 1, d_width)])


    def lin_solve(self, d_width, b, x, x0, a, c):
        for k in range(5):
            for i in range(1, d_width + 1):
                for j in range(1, d_width + 1):
                    x[self.xy_coordinate(d_width, i, j)] = (x0[self.xy_coordinate(d_width, i, j)] + a * (x[self.xy_coordinate(d_width, i - 1, j)] + x[
                        self.xy_coordinate(d_width, i + 1, j)] + x[self.xy_coordinate(d_width, i, j - 1)] + x[self.xy_coordinate(d_width, i, j + 1)])) / c
                    
            # self.set_bounds(d_width, b, x)

    def diffuse(self, d_width, b, dens, dens_prev, d_rate, time_space):
        coefficient = time_space * d_rate * (d_width ** 2)
        self.lin_solve(d_width, b, dens, dens_prev, coefficient, 1 + 4 * coefficient)

    # u = horizontal velocity; v = vertical velocity
    def advect(self, d_width, b, dens, dens_prev, u, v, time_space):
        time_space0 = time_space * d_width

        for i in xrange(1, d_width + 1):
            for j in xrange(1, d_width + 1):
                x = i - time_space0 * u[self.xy_coordinate(d_width, i, j)]
                y = j - time_space0 * v[self.xy_coordinate(d_width, i, j)]

                if(x < 0.5):
                    x = 0.5
                if(x > d_width + 0.5):
                    x = d_width + 0.5

                i0 = int(x)
                i1 = i0 + 1

                if(y < 0.5):
                    y = 0.5
                if(y > d_width + 0.5):
                    y = d_width + 0.5

                j0 = int(y)
                j1 = j0 + 1

                s1 = x - i0
                s0 = 1 - s1
                t1 = y - j0
                t0 = 1 - t1

                tmp = s0 * (t0 * dens_prev[self.xy_coordinate(d_width, i0, j0)] + t1 * dens_prev[self.xy_coordinate(d_width, i0, j1)])
                dens[self.xy_coordinate(d_width, i, j)] = tmp + s1 * (t0 * dens_prev[self.xy_coordinate(d_width, i1, j0)] + t1 * dens_prev[self.xy_coordinate(d_width, i1, j1)])

        # self.set_bounds(d_width, b, dens)

    def swap(self, x0, x):
        tmp = x0
        x0 = x
        x = tmp
        return x0, x

    def projection(self, d_width, u, v, p, div):
        h = 1.0 / d_width

        for i in xrange(1, d_width + 1):
            for j in xrange(1, d_width + 1):
                uv_sum = u[self.xy_coordinate(d_width, i + 1, j)] - u[self.xy_coordinate(d_width, i - 1, j)] + v[self.xy_coordinate(d_width, i, j + 1)] - v[self.xy_coordinate(d_width, i, j - 1)]
                div[self.xy_coordinate(d_width, i, j)] = -0.5 * uv_sum * h
                p[self.xy_coordinate(d_width, i, j)] = 0

#         self.set_bounds(d_width, 0, div)
#         self.set_bounds(d_width, 0, p)

        self.lin_solve(d_width, 0, p, div, 1, 4)

        for i in xrange(1, d_width + 1):
            for j in xrange(1, d_width + 1):
                u[self.xy_coordinate(d_width, i, j)] -= 0.5 / h * (
                    p[self.xy_coordinate(d_width, i + 1, j)] - p[self.xy_coordinate(d_width, i - 1, j)])
                v[self.xy_coordinate(d_width, i, j)] -= 0.5 / h * (
                    p[self.xy_coordinate(d_width, i, j + 1)] - p[self.xy_coordinate(d_width, i, j - 1)])

        # self.set_bounds(d_width, 1, u)
        # self.set_bounds(d_width, 2, v)

    '''
    DENSITY SOLVER
    '''

    # u = horizontal velocity; v = vertical velocity

    def density_step(self, d_width, dens, dens_prev, u, v, d_rate, time_space):
        self.add_source(dens, dens_prev, time_space)
        dens, dens_prev = self.swap(dens, dens_prev)
        
        self.diffuse(d_width, 0, dens, dens_prev, d_rate, time_space)
        dens, dens_prev = self.swap(dens, dens_prev)

        # start = time.time()
        self.advect(d_width, 0, dens, dens_prev, u, v, time_space)
        # endt = time.time()
        
        # print("Advect: ", endt - start)

        return dens, dens_prev

    '''
    VELOCITY SOLVER
    '''

    def velocity_step(self, d_width, u, v, u0, v0, visc, time_space):
        
        self.add_source(u, u0, time_space)
        self.add_source(v, v0, time_space)

        u0, u = self.swap(u0, u)
        self.diffuse(d_width, 1, u, u0, visc, time_space)

        v0, v = self.swap(v0, v)
        self.diffuse(d_width, 2, v, v0, visc, time_space)
        
        # start = time.time()
        self.projection(d_width, u, v, u0, v0)
        # endt = time.time()
        # print("Projection: ", endt - start)
        
        u0, u = self.swap(u0, u)
        v0, v = self.swap(v0, v)

        self.advect(d_width, 1, u, u0, u0, v0, time_space)
        self.advect(d_width, 2, v, v0, u0, v0, time_space)

        self.projection(d_width, u, v, u0, v0)

        return u, v, u0, v0
