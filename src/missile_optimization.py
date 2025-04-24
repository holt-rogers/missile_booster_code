from math import log, pi, e
import dearpygui.dearpygui as dpg

# lowest found veliocity : used for plot configuration by GUI
lowest_v = float("inf")

# constraints to the rocket
min_size = 0
max_size = 1

g =  9.80665

# set the global optimization constraints
def set_constraints(mn, mx):
    global min_size, max_size
    min_size = mn
    max_size = mx


def calculate_propellent_mass(height, diameter, density):
    # volume of cylinder times density
    return height * (diameter/2)**2 * pi * density

def find_structure_mass(efficiency, payload, propellent): #takes structural efficiency, which is an indicator of the amount of stress a structure can take for the mass
    if efficiency == 0:                                   #and determines what the structural mass would be based on the non structural mass (payload + propellant)
        return 0
    return (propellent + payload)/ efficiency 

def get_lowest_v(): # getter functions so the UI can access lowest_v V for plot settings
    return lowest_v

# this functions returns the ideal mass fractions for a rocket without a booster stage
def optimize_mass_fraction(isp, payload, mass_structure, mass_propellant, heatmap = []):
    global lowest_v
    global min_size, max_size

    best_v = float("-inf") 
    best_ratios = []



    # looping through the possible range of fuel we can use 
    for mf2 in range(1000, -1, -1): #mr1 = mass ratio for pop out booster/first stage. mr2 = mass ratio for second stage. mr3 = mass ratio for 3rd stage
        for mf1 in range(0, 1001):

            # calculate last mass fractions
            mf3 = 1000 - mf1 - mf2

            # add a value of 0 to the heatmap and skip if this rocket is not possible
            if mf3 <= 0:
                if (mf1 - 1) % 10 == 0 and (mf2 - 1) % 10 == 0:
                    heatmap.append(0)
                continue

        
            # turn the integers into proportions
            mf1_2, mf2_2, mf3_2 = mf1/1000, mf2/1000, mf3/1000
            v = sum(list(delta_v(mf1_2, mf2_2, mf3_2, isp, payload, mass_structure, mass_propellant)))
            if (mf1 - 1) % 10 == 0 and (mf2 - 1) % 10 == 0:
                heatmap.append(v) # add data of optimization to create heatmap where the heat gradient shows where the most optimized results are

            # compare to current best
            if v > best_v:
                if max([mf1_2, mf2_2, mf3_2]) <= max_size and  min([mf1_2, mf2_2, mf3_2]) >= min_size:
                    best_v = v
                    best_ratios = [mf1_2, mf2_2, mf3_2]
            if v < lowest_v:
                lowest_v = v

    return best_ratios

# optimizes the mass fractions for a rocket with a booster stage 
def optimize_booster(isp, payload, mass_structure, mass_propellant, time_to_burn, booster_v = [], booster_ratio=[]):
    # calculate mass ratio of the booster stage

    global min_size, max_size

    # calculate the size of the booster stage
    mf1 = (mass_propellant + mass_structure + payload) * (1  - e**(-time_to_burn/(2*isp))) / mass_propellant
    mf1 = max([min_size, mf1])
    mf1 = min([max_size, mf1])

    # used to determine the optimized value
    best_v = float("-inf")
    best_ratios = []

    # loop through proportions for stage 2
    for proportion in range(0, 1001):
        # calculate stage 2 and 3 mass fractionsd
        mf2 = proportion/1000
        mf3 = 1 - mf2 - mf1

        # if the rocket is not possible
        if mf3 < 0:
            continue

        v = sum(list(delta_v(mf1, mf2, mf3, isp, payload, mass_structure, mass_propellant)))
        # add data for optimization graph
        booster_v.append(v)
        booster_ratio.append(mf2)
        # store if the highest velocity 
        if v > best_v:
            if max([mf1, mf2, mf3]) <= max_size and  min([mf1, mf2, mf3]) >= min_size:
                best_v = v
                best_ratios = [mf1, mf2, mf3]
    return best_ratios

# returns a list of the chagne in velocity for each stage 
def delta_v(mf1, mf2, mf3, isp, payload, mass_structure, mass_propellent):
    global g

    pl = payload
    
    # mass of propllent for each stage
    mp1 = mf1 * mass_propellent
    mp2 = mf2 * mass_propellent
    mp3 = mf3 * mass_propellent

    # mass of structure for each stage 
    ms1 = mf1 * mass_structure
    ms2 = mf2 * mass_structure
    ms3 = mf3 * mass_structure

    # calculate velocity change at each stage using Tsiolkovsky rocket equation
    v3 = g * isp * log(1 + mp3/(ms3 + pl))
    v2 = g * isp * log(1 + mp2/(mp3 + ms3 + ms2 + pl))
    v1 = g * isp * log(1 + mp1/(mp3 + ms3 + mp2 + ms2 + ms1 + pl))
    

    return v1, v2, v3

# returns the mass ratios
# defined as final mass over initial mass of each stage
def mass_ratios(mf1, mf2, mf3, payload, mass_structure, mass_propellent):
    pl = payload
    mp1 = mf1 * mass_propellent
    mp2 = mf2 * mass_propellent
    mp3 = mf3 * mass_propellent

    ms1 = mf1 * mass_structure
    ms2 = mf2 * mass_structure
    ms3 = mf3 * mass_structure


    mr3 = 1 + mp3/(ms3 + pl)
    mr2 = 1 + mp2/(mp3 + ms3 + ms2 + pl)
    mr1 = 1 + mp1/(mp3 + ms3 + mp2 + ms2 + ms1 + pl)

    return mr1, mr2, mr3

# generates a data showing the velocity as propellent is used
def generate_trajectory(mf1, mf2, mf3, isp, payload, mass_structure, mass_propellent, x_points, y_points):
    global g

    # points in the graph
    point_count = 1000

    pl = payload
    v1, v2, v3 = delta_v(mf1, mf2, mf3, isp, payload, mass_structure, mass_propellent)

    ms1 = mf1 * mass_structure
    ms2 = mf2 * mass_structure
    ms3 = mf3 * mass_structure

    mp1 = mf1 * mass_propellent
    mp2 = mf2 * mass_propellent
    mp3 = mf3 * mass_propellent

    # for each point
    for i in range(1,point_count+1):
        x = mass_propellent * i / point_count
        y = 0

        # calculate piece wise function depending on stage progression
        if i/point_count < mf1:
            mp = mass_propellent * i/point_count
            y = g * isp * log(1 + mp /(mp3 + ms3 + mp2 + ms2 + ms1 + pl))
        elif i/point_count < mf1 + mf2:
            mp = mass_propellent * (i/point_count - mf1)
            y = v1 + g * isp * log(1 + mp /(mp3 + ms3 + ms2 + pl))
        else:
            mp = mass_propellent * (i/point_count - mf1 - mf2)
            y = v1 + v2 + g * isp * log(1 + mp/(ms3 + pl))

        # add points to the graph
        x_points.append(x)
        y_points.append(y)
