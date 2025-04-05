from math import log
import dearpygui.dearpygui as dpg



def optimize_mass_ratio(isp, payload, booster = False, time_to_burn = None, graph = None):
    mass_propellant = 1500
    mass_structure = 500
    structural_efficiency = 0.1

    best_v = float("-inf")
    best_ratios = []

    speeds = []
    ratios = []

    if booster:
        return 0.2, 0.5, 0.3
    else:
        # looping through the possible range of fuel we can use 
        for mr1 in range(300, 999):
            for mr2 in range(1, 1000 - mr1):
                mr3 = 1000 - mr1 - mr2
                # first has to be largest
                if mr1 <= mr2:
                    continue
                elif mr2 <= mr3:
                    continue

                mr1, mr2, mr3 = mr1/1000, mr2/1000, mr3/1000





                v = sum(delta_v(mr1, mr2, mr3, isp, payload, mass_structure, mass_propellant))
                if v > best_v:
                    best_v = v
                    best_ratios = [mr1, mr2, mr3]

                speeds.append(v)
                ratios.append(mr1)


        if graph != None:
            with dpg.plot(parent=graph, label="TEST", height=300, width=600):
                dpg.add_plot_axis(dpg.mvXAxis, label="x", tag  ="x_axis")
                dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="y_axis")
                dpg.add_line_series(ratios, speeds, parent="y_axis")
        return best_ratios

# note m1, m2 and m3 are equal to 

def delta_v(mr1, mr2, mr3, isp, payload, mass_structure, mass_propellent):
    g =  9.80665
    
    mp1 = mr1 * mass_propellent
    mp2 = mr2 * mass_propellent
    mp3 = mr3 * mass_propellent

    ms1 = mr1 * mass_structure
    ms2 = mr2 * mass_structure
    ms3 = mr3 * mass_structure

    # shorten bc typing is for losers
    pl = payload

    v3 = g * isp * log(1 + mp3 /(ms3 + pl))
    v2 = g * isp * log(1 + mp2/(mp3 + ms3 + ms2 + pl))
    v1 = g * isp * log(1 + mp1/(mp3 + ms3 + mp2 + ms2 + ms1 + pl))
    


    return v1, v2, v3

