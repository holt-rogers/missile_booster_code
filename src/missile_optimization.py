from math import log
import dearpygui.dearpygui as dpg



def optimize_mass_ratio(isp, payload, booster = False, time_to_burn = None, graph = None):
    mass_propellant = 1500
    structural_efficiency = 0.1

    best_v = float("-inf")
    best_ratios = []

    speeds = []
    ratios = []

    if booster:
        return 0.2, 0.5, 0.3
    else:
        # looping through the possible range of fuel we can use 
        for mr3 in range(334, 998):
            for mr2 in range(int((1000 - mr3)/2),1000 - mr3):
                mp3 = mr3/1000 
                mp2 = mr2/1000
                mp1 = 1 - mp3 - mp2


                if mp3 < 0.1 or mp3 > 0.8:
                    continue
                elif mp2 < 0.1 or mp2 > 0.8:
                    continue
                elif mp1 < 0.1 or mp1 > 0.8:
                    continue

                # load
                ml1 = payload + mp1*mass_propellant
                # structure
                ms1 = ml1 * structural_efficiency
                # total
                m1 = ms1 + ml1

                ml2 =  mp2*mass_propellant + m1
                ms2 = ml2 * structural_efficiency
                m2 = ms2 + ml2

                ml3 = mp3*mass_propellant + m2
                ms3 = ml3 * structural_efficiency
                m3 = ms3 + ml3


                v = sum(delta_v(m1, m2, m3,payload,isp))
                if v > best_v:
                    best_v = v
                    best_ratios = ([mp3, mp2, mp1])

                speeds.append(v)
                ratios.append(mr3)

        if graph != None:
            with dpg.plot(parent=graph, label="TEST", height=300, width=600):
                dpg.add_plot_axis(dpg.mvXAxis, label="x", tag  ="x_axis")
                dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="y_axis")
                dpg.add_line_series(ratios, speeds, parent="y_axis")
        return best_ratios

# note m1, m2 and m3 are equal to 

def delta_v(m1, m2, m3, payload,isp):
    g =  9.80665
    v1 = g * isp * log((m1/ payload))
    v2 = g * isp * log((m2/ payload))
    v3 = g * isp * log((m3/ payload))

    return v1, v2, v3

