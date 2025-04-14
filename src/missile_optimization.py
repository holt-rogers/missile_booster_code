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
def optimize_mass_ratio(isp, payload, mass_structure, mass_propellant, heatmap = []):
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


def optimize_booster(isp, payload, mass_structure, mass_propellant, time_to_burn, booster_v = []):
    # calculate mass ratio of the booster stage
    mr1 = (mass_propellant + mass_structure + payload) * (1  - e**(-time_to_burn/(2*isp))) / mass_propellant

    best_v = float("-inf")
    best_ratios = []

    for proportion in range(0, 1001):
        mr2 = proportion/1000
        mr3 = 1 - mr2 - mr1
        if mr3 <= 0:
            continue

        v = sum(list(delta_v(mr1, mr2, mr3, isp, payload, mass_structure, mass_propellant)))
        booster_v.append(v)
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
    #print(mp3, ms3, pl)
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

def generate_trajectory(mr1, mr2, mr3, isp, payload, mass_structure, mass_propellent, x_points, y_points):
    point_count = 1000
    g = 9.8
    pl = payload
    v1, v2, v3 = delta_v(mr1, mr2, mr3, isp, payload, mass_structure, mass_propellent)

    ms1 = mr1 * mass_structure
    ms2 = mr2 * mass_structure
    ms3 = mr3 * mass_structure

    mp1 = mr1 * mass_propellent
    mp2 = mr2 * mass_propellent
    mp3 = mr3 * mass_propellent

    for i in range(1,point_count+1):
        x = mass_propellent * i / point_count
        y = 0
        # see which stage we are on
        if i/point_count < mr1:
            mp = mass_propellent * i/point_count
            y = g * isp * log(1 + mp /(mp3 + ms3 + mp2 + ms2 + ms1 + pl))
        elif i/point_count < mr1 + mr2:
            mp = mass_propellent * (i/point_count - mr1)
            y = v1 + g * isp * log(1 + mp /(mp3 + ms3 + ms2 + pl))
        else:
            mp = mass_propellent * (i/point_count - mr1 - mr2)
            y = v1 + v2 + g * isp * log(1 + mp/(ms3 + pl))

        x_points.append(x)
        y_points.append(y)
