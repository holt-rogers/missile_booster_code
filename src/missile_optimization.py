from math import log, pi, e
import dearpygui.dearpygui as dpg

lowest_v = float("inf")
def calculate_propellent_mass(height, diameter, density):
    # volume of cylinder times density
    return height * (diameter/2)**2 * pi * density

def find_structure_mass(efficiency, payload, propellent):
    return (propellent + payload)/ efficiency

def get_lowest_v():
    return lowest_v

# this functions returns the proportion of each size
# the name is really misleading, my bad
def optimize_mass_ratio(isp, payload, mass_structure, mass_propellant, heatmap = [], graph = None):
    global lowest_v

    best_v = float("-inf") 
    best_ratios = []



    # looping through the possible range of fuel we can use 
    for mr2 in range(1000, -1, -1):
        for mr1 in range(0, 1001):
            
            mr3 = 1000 - mr1 - mr2
            if mr3 <= 0:
                if (mr1 - 1) % 10 == 0 and (mr2 - 1) % 10 == 0:
                    heatmap.append(0)
                continue
            # first has to be largest

            mr1_2, mr2_2, mr3_2 = mr1/1000, mr2/1000, mr3/1000
            v = sum(list(delta_v(mr1_2, mr2_2, mr3_2, isp, payload, mass_structure, mass_propellant)))
            if (mr1 - 1) % 10 == 0 and (mr2 - 1) % 10 == 0:
                heatmap.append(v)
            #heatmap.append(v)
            if v > best_v:
                best_v = v
                best_ratios = [mr1_2, mr2_2, mr3_2]
            if v < lowest_v:
                lowest_v = v

    return best_ratios

'''
        if graph != None:
            with dpg.plot(parent=graph, label="TEST", height=300, width=600):
                dpg.add_plot_axis(dpg.mvXAxis, label="x", tag  ="x_axis")
                dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="y_axis")
                dpg.add_line_series(ratios, speeds, parent="y_axis")
        return best_ratios
'''

def optimize_booster(isp, payload, mass_structure, mass_propellant, time_to_burn, graph = None):
    # calculate mass ratio of the booster stage
    mr1 = (mass_propellant + mass_structure + payload) * (1  - e**(-time_to_burn/(2*isp))) / mass_propellant

    best_v = float("-inf")
    best_ratios = []

    for proportion in range(0, 1001):
        mr2 = proportion/1000
        mr3 = 1 - mr2 - mr1

        v = sum(list(delta_v(mr1, mr2, mr3, isp, payload, mass_structure, mass_propellant)))

        if v > best_v:
            best_v = v
            best_ratios = [mr1, mr2, mr3]
    return best_ratios





def delta_v(mr1, mr2, mr3, isp, payload, mass_structure, mass_propellent):
    g =  9.80665
    pl = payload
    
    mp1 = mr1 * mass_propellent
    mp2 = mr2 * mass_propellent
    mp3 = mr3 * mass_propellent

    ms1 = mr1 * mass_structure
    ms2 = mr2 * mass_structure
    ms3 = mr3 * mass_structure


    # shorten bc typing is for losers

    v3 = g * isp * log(1 + mp3/(ms3 + pl))
    v2 = g * isp * log(1 + mp2/(mp3 + ms3 + ms2 + pl))
    v1 = g * isp * log(1 + mp1/(mp3 + ms3 + mp2 + ms2 + ms1 + pl))
    


    return v1, v2, v3


def mass_ratios(stage1, stage2, stage3, payload, mass_structure, mass_propellent):
    pl = payload
    mp1 = stage1 * mass_propellent
    mp2 = stage2 * mass_propellent
    mp3 = stage3 * mass_propellent

    ms1 = stage1 * mass_structure
    ms2 = stage2 * mass_structure
    ms3 = stage3 * mass_structure


    mr3 = 1 + mp3/(ms3 + pl)
    mr2 = 1 + mp2/(mp3 + ms3 + ms2 + pl)
    mr1 = 1 + mp1/(mp3 + ms3 + mp2 + ms2 + ms1 + pl)

    return mr1, mr2, mr3



