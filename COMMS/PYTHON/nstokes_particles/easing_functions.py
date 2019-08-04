import math

def easelist():
    return [256.0, 255.998976, 255.991808, 255.972352, 255.934464, 255.872, 255.778816, 255.648768, 255.475712, 255.253504, 254.976, 254.637056, 254.230528, 253.750272, 253.190144, 252.544, 251.805696, 250.969088, 250.028032, 248.976384, 247.808, 246.516736, 245.096448, 243.540992, 241.844224, 240.0, 238.002176, 235.844608, 233.521152, 231.025664, 228.352, 225.494016, 222.44556799999998, 219.200512, 215.752704, 212.096, 208.224256, 204.131328, 199.811072, 195.257344, 190.464, 185.424896, 180.13388799999998, 174.584832, 168.77158399999996, 162.688, 156.32793599999997, 149.68524799999997, 142.75379199999992, 135.52742399999997, 128.0, 120.472576, 113.246208, 106.314752, 99.67206399999998, 93.31199999999995, 87.22841599999998, 81.41516799999997, 75.86611199999996, 70.57510399999995, 65.536, 60.742655999999954, 56.188928000000004, 51.86867199999995, 47.775744, 43.903999999999996, 40.247296000000006, 36.799488, 33.55443199999999, 30.505983999999984, 27.648000000000025, 24.974335999999994, 22.478848, 20.155391999999978, 17.99782400000001, 16.0, 14.155776000000003, 12.459007999999983, 10.90355199999999, 9.483263999999991, 8.192000000000007, 7.023616000000004, 5.971968000000004, 5.030912000000001, 4.194303999999988, 3.455999999999989, 2.8098559999999964, 2.2497280000000046, 1.7694720000000075, 1.3629439999999988, 1.024000000000001, 0.7464960000000076, 0.5242879999999843, 0.3512320000000102, 0.22118399999999383, 0.12800000000001432, 0.0655360000000087, 0.02764799999999923, 0.008192000000008193, 0.001024000000001024]

class EasingBase:
    limit = (0, 1)

    def __init__(self, start=0, end=1, duration=1):
        self.start = start
        self.end = end
        self.duration = duration

    @classmethod
    def func(cls, t):
        raise NotImplementedError

    def ease(self, alpha):
        t = self.limit[0] * (1 - alpha) + self.limit[1] * alpha
        t /= self.duration
        a = self.func(t)
        return self.end * a + self.start * (1 - a)


"""
Quadratic easing functions
"""


class QuadEaseInOut(EasingBase):
    def func(self, t):
        if t < 0.5:
            return 2 * t * t
        return (-2 * t * t) + (4 * t) - 1


class QuadEaseIn(EasingBase):
    def func(self, t):
        return t * t


class QuadEaseOut(EasingBase):
    def func(self, t):
        return -(t * (t - 2))


"""
Cubic easing functions
"""


class CubicEaseIn(EasingBase):
    def func(self, t):
        return t * t * t


class CubicEaseOut(EasingBase):
    def func(self, t):
        return (t - 1) * (t - 1) * (t - 1) + 1


class CubicEaseInOut(EasingBase):
    def func(self, t):
        if t < 0.5:
            return 4 * t * t * t
        p = 2 * t - 2
        return 0.5 * p * p * p + 1


"""
Quartic easing functions
"""


class QuarticEaseIn(EasingBase):
    def func(self, t):
        return t * t * t * t


class QuarticEaseOut(EasingBase):
    def func(self, t):
        return (t - 1) * (t - 1) * (t - 1) * (1 - t) + 1


class QuarticEaseInOut(EasingBase):
    def func(self, t):
        if t < 0.5:
            return 8 * t * t * t * t
        p = t - 1
        return -8 * p * p * p * p + 1


"""
Quintic easing functions
"""


class QuinticEaseIn(EasingBase):
    def func(self, t):
        return t * t * t * t * t


class QuinticEaseOut(EasingBase):
    def func(self, t):
        return (t - 1) * (t - 1) * (t - 1) * (t - 1) * (t - 1) + 1


class QuinticEaseInOut(EasingBase):
    def func(self, t):
        if t < 0.5:
            return 16 * t * t * t * t * t
        p = (2 * t) - 2
        return 0.5 * p * p * p * p * p + 1


"""
Sine easing functions
"""


class SineEaseIn(EasingBase):
    def func(self, t):
        return math.sin((t - 1) * math.pi / 2) + 1


class SineEaseOut(EasingBase):
    def func(self, t):
        return math.sin(t * math.pi / 2)


class SineEaseInOut(EasingBase):
    def func(self, t):
        return 0.5 * (1 - math.cos(t * math.pi))


"""
Circular easing functions
"""


class CircularEaseIn(EasingBase):
    def func(self, t):
        return 1 - math.sqrt(1 - (t * t))


class CircularEaseOut(EasingBase):
    def func(self, t):
        return math.sqrt((2 - t) * t)


class CircularEaseInOut(EasingBase):
    def func(self, t):
        if t < 0.5:
            return 0.5 * (1 - math.sqrt(1 - 4 * (t * t)))
        return 0.5 * (math.sqrt(-((2 * t) - 3) * ((2 * t) - 1)) + 1)


"""
Exponential easing functions
"""


class ExponentialEaseIn(EasingBase):
    def func(self, t):
        if t == 0:
            return 0
        return math.pow(2, 10 * (t - 1))


class ExponentialEaseOut(EasingBase):
    def func(self, t):
        if t == 1:
            return 1
        return 1 - math.pow(2, -10 * t)


class ExponentialEaseInOut(EasingBase):
    def func(self, t):
        if t == 0 or t == 1:
            return t

        if t < 0.5:
            return 0.5 * math.pow(2, (20 * t) - 10)
        return -0.5 * math.pow(2, (-20 * t) + 10) + 1


"""
Elastic Easing Functions
"""


class ElasticEaseIn(EasingBase):
    def func(self, t):
        return math.sin(13 * math.pi / 2 * t) * math.pow(2, 10 * (t - 1))


class ElasticEaseOut(EasingBase):
    def func(self, t):
        return math.sin(-13 * math.pi / 2 * (t + 1)) * math.pow(2, -10 * t) + 1


class ElasticEaseInOut(EasingBase):
    def func(self, t):
        if t < 0.5:
            return (
                0.5
                * math.sin(13 * math.pi / 2 * (2 * t))
                * math.pow(2, 10 * ((2 * t) - 1))
            )
        return 0.5 * (
            math.sin(-13 * math.pi / 2 * ((2 * t - 1) + 1))
            * math.pow(2, -10 * (2 * t - 1))
            + 2
        )


"""
Back Easing Functions
"""


class BackEaseIn(EasingBase):
    def func(self, t):
        return t * t * t - t * math.sin(t * math.pi)


class BackEaseOut(EasingBase):
    def func(self, t):
        p = 1 - t
        return 1 - (p * p * p - p * math.sin(p * math.pi))


class BackEaseInOut(EasingBase):
    def func(self, t):
        if t < 0.5:
            p = 2 * t
            return 0.5 * (p * p * p - p * math.sin(p * math.pi))

        p = 1 - (2 * t - 1)

        return 0.5 * (1 - (p * p * p - p * math.sin(p * math.pi))) + 0.5


"""
Bounce Easing Functions
"""


class BounceEaseIn(EasingBase):
    def func(self, t):
        return 1 - BounceEaseOut().func(1 - t)


class BounceEaseOut(EasingBase):
    def func(self, t):
        if t < 4 / 11:
            return 121 * t * t / 16
        elif t < 8 / 11:
            return (363 / 40.0 * t * t) - (99 / 10.0 * t) + 17 / 5.0
        elif t < 9 / 10:
            return (4356 / 361.0 * t * t) - (35442 / 1805.0 * t) + 16061 / 1805.0
        return (54 / 5.0 * t * t) - (513 / 25.0 * t) + 268 / 25.0


class BounceEaseInOut(EasingBase):
    def func(self, t):
        if t < 0.5:
            return 0.5 * BounceEaseIn().func(t * 2)
        return 0.5 * BounceEaseOut().func(t * 2 - 1) + 0.5
