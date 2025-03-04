from math import log

# TODO, impliment me

def optimize_mass_ratio(isp, payload, booster = False, time_to_burn = None):
    if booster:
        return 0.2, 0.5, 0.3
    else:
        return 0.1, 0.2, 0.7

def delta_v(m1, m2, m3, isp):
    g =  9.80665

    v1 = g * isp * log(m1)
    v2 = g * isp * log(m2)
    v3 = g * isp * log(m3)

    return v1, v2, v3

