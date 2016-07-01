import math

def green_ampt_cum_infiltration(rain, psi, eff_theta,eff_sat, K, dt):
    import math
    no_of_loops_to_solve = max(dt, 1000.0)
    psi = abs(psi)
    con = psi * (eff_sat - eff_theta)
    if rain == 0:
        F = 0
    elif (rain - K) <= 0:
        F = rain * dt
    elif (rain - K) > 0:
        # calculate the infiltration until the ponding
        F_p = K * con /  (rain - K)

        # calculate ponding time
        t_p = F_p / rain

        if dt <= t_p:
            F = dt * rain
        else:
            lowest_error = 1000
            for i in range(1,int(no_of_loops_to_solve)):
                # i is rain multiplied by 1000
                F_guess = i/float(no_of_loops_to_solve) * rain*dt
                t_guess = t_p + 1/K * (F_guess - F_p + con * math.log((con+F_p)/(con + F_guess)) )

                error = abs(t_guess - dt)
                # print " i:%s \t, F_p: %s, t_p: %s, F_guess:%s,  t_guess:%s and error:%s " %(i, F_p, t_p,F_guess, t_guess, error)
                if error < lowest_error:
                    lowest_error = error
                    F = F_guess
                    if error < 1:
                        break
    if F is None:
        return F_guess
    return F

# RBC_simulation
rain = 50
psi = 288.75
eff_theta = 0.3796
eff_sat = 0.9
K = 0.03828
dt = 86400

# # eg_simulation
# rain = 0.000335
# psi = 21449.9
# eff_theta = 0.374
# eff_sat = 0.536
# K = 0.0366
# dt = 21600

print "the green ampt infiltration depth is ", green_ampt_cum_infiltration(rain, psi, eff_theta,eff_sat, K, dt)