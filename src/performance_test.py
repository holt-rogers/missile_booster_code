import time
from missile_optimization import *
import matplotlib.pyplot as plt

# simple script to test and log the performance based on changing variables

# default oprimization variables
time_to_burn = 10
payload = 250
height = 10
diameter = 1
density = 1500 # find source
isp = 300
structural_efficiency = 4

diamter_test = []
time_diamter = []

height_test = []
time_height = []





# returns time for given optimization
def test_optimization(height, diameter):
    global structural_efficiency, time_to_burn, payload, density, isp
    #set_constraints(min_ratio, max_ratio)
    start_time = time.perf_counter()

    propllent_mass = calculate_propellent_mass(height, diameter, density)
    structure_mass = find_structure_mass(structural_efficiency, payload, propllent_mass)
    stage_r1, stage_r2, stage_r3 = optimize_mass_ratio(isp, payload, structure_mass, propllent_mass, heatmap=[])
    stage_r1, stage_r2, stage_r3 = round(stage_r1, 3), round(stage_r2,3), round(stage_r3,3)
    bstage_r1, bstage_r2, bstage_r3 = optimize_booster(isp, payload, structure_mass, propllent_mass, time_to_burn, booster_v=[], booster_ratio=[])
    bstage_r1, bstage_r2, bstage_r3 = round(bstage_r1, 3), round(bstage_r2,3), round(bstage_r3,3)
    generate_trajectory(stage_r1, stage_r2, stage_r3, isp, payload,structure_mass, propllent_mass, [], [])
    generate_trajectory(bstage_r1, bstage_r2, bstage_r3, isp, payload,structure_mass, propllent_mass, [], [])

    return time.perf_counter() - start_time


# test different diameters
for i in range(1, 101):
    diamter_test.append(i)
    time_diamter.append(test_optimization(height, i))
    print(i / 200 * 100, "%")

for i in range(1, 101):
    height_test.append(i)
    time_height.append(test_optimization(height, i))
    print((i + 100)/200 * 100, "%")

plt.plot(diamter_test, time_diamter, color = "blue", label = "Diamter")
plt.plot(height_test, time_height, color = "orange", label = "Height")

# Add title and labels
plt.title('Change in Runtime as Rocket Size Increases')
plt.xlabel('Length (m)')
plt.ylabel('Optimization (s)')

print("Average time: ", sum(time_height + time_diamter) / (len(time_diamter) + len(time_height)))

print("DONE")
plt.show()