import dearpygui.dearpygui as dpg
from missile_optimization import *
from dearpygui_ext.themes import create_theme_imgui_light

dpg.create_context()

# defualt rocket problem
# based on information given by client
time_to_burn = 10
payload = 250
height = 10
diameter = 1

# rocket constants
density = 1600 # average of the density range for AP-HTPB solid propellent, commonly used in rocket fuel 
#https://www.sciencedirect.com/science/article/pii/S1878535215000106#b0020

isp = 265 # using ISP for Al-AP-HTPB propellent, a common solid rocket fuel used in rockets such as the SM-3
#https://www.generalstaff.org/BBOW/Progs/FlySIM/SM3_Thesis.pdf

structural_efficiency = 4


# mass fractions for each stage. with and without boster
mf1, mf2, mf3 = 0,0,0
bmf1, bmf2, bmf3 = 0.2, 0.5, 0.3

# storage for graph data and tables
table = []
b_table = []
total_v = None
btotal_v = None
bdifference_v = None

heatmap_v = []
booster_v = []
booster_ratio = []

x_propellent = []
graph_velocity = []
graph_booster_velocity = []

# mass fraction constraints
min_fraction = 0.1
max_fraction = 0.8

# called whenever user clicks Update Optimization
def on_click():
    global mf1, mf2, mf3, isp, payload, time_to_burn, table, bmf1, bmf2, bmf3
    global diameter, height, density, structural_efficiency, heatmap_v, booster_v, booster_ratio
    
    # clear old graph data
    heatmap_v.clear()
    booster_v.clear()
    booster_ratio.clear()

    # update values from input boxes
    isp = dpg.get_value("isp")
    payload = dpg.get_value("payload")
    time_to_burn = dpg.get_value("burn_time")
    density = dpg.get_value("density")
    height = dpg.get_value("height")
    diameter = dpg.get_value("diameter")
    structural_efficiency = dpg.get_value("efficiency")
    min_fraction = dpg.get_value("min")
    max_fraction = dpg.get_value("max")

    # set mass fraction constraints
    if dpg.get_value("constrained"):
        set_constraints(min_fraction, max_fraction)
    else:
        set_constraints(0,1)


    # calculated optimied data
    propllent_mass = calculate_propellent_mass(height, diameter, density)
    structure_mass = find_structure_mass(structural_efficiency, payload, propllent_mass)

    bmf1, bmf2, bmf3 = optimize_booster(isp, payload, structure_mass, propllent_mass, time_to_burn, booster_v=booster_v, booster_ratio=booster_ratio)
    mf1, mf2, mf3 = optimize_mass_fraction(isp, payload, structure_mass, propllent_mass, heatmap=heatmap_v)
    mf1, mf2, mf3 = round(mf1, 3), round(mf2,3), round(mf3,3)

    # update visuals
    update_mass_ratio_fraction()
    update_table() 
    update_graph()


# updates the visual representations of the mass fractions (Visualzitions window)
def update_mass_ratio_fraction():
    global mf1, mf2, mf3, bmf1, bmf2, bmf3

    # offset of rockets
    pos_x = 30
    pos_y = 10

    # total dimensions of the rocket
    width = 30
    height = 150

    # calculate top left and bottom right for each stage
    pos3min = [pos_x, pos_y]
    pos3max = [pos_x + width, pos_y + mf3*height]

    pos2min = [pos_x, pos3max[1]]
    pos2max = [pos_x + width, pos2min[1] + height * mf2]

    pos1min = [pos_x, pos2max[1]]
    pos1max = [pos_x + width, pos1min[1] + height * mf1]

    # visualization colors
    border_color = (0,0,0,255)

    color1 = (144, 169, 237, 255)
    color2 = (182, 198, 242, 255)
    color3 = (219, 227, 248, 255)

    # update rectangles
    dpg.configure_item("mr1", pmin=pos1min, pmax=pos1max, color=border_color, thickness=1, fill=color1)
    dpg.configure_item("mr2", pmin=pos2min, pmax=pos2max, color=border_color, thickness=1, fill=color2)
    dpg.configure_item("mr3", pmin=pos3min, pmax=pos3max, color=border_color, thickness=1, fill=color3)

    dpg.configure_item("mr1_text", text="S1", pos = (pos1max[0] + 10, (pos1min[1] + pos1max[1])/2 -6), size = 12)
    dpg.configure_item("mr2_text", text="S2", pos = (pos2max[0] + 10, (pos2min[1] + pos2max[1])/2 -6), size = 12)
    dpg.configure_item("mr3_text", text="S3", pos = (pos3max[0] + 10, (pos3min[1] + pos3max[1])/2 -6), size = 12)

    # repeate for booster stage
    pos3min = [pos_x, pos_y]
    pos3max = [pos_x + width, pos_y + bmf3*height]

    pos2min = [pos_x, pos3max[1]]
    pos2max = [pos_x + width, pos2min[1] + height * bmf2]

    pos1min = [pos_x, pos2max[1]]
    pos1max = [pos_x + width, pos1min[1] + height * bmf1]

    dpg.configure_item("mr1b", pmin=pos1min, pmax=pos1max, color=border_color, thickness=1, fill=color1)
    dpg.configure_item("mr2b", pmin=pos2min, pmax=pos2max, color=border_color, thickness=1, fill=color2)
    dpg.configure_item("mr3b", pmin=pos3min, pmax=pos3max, color=border_color, thickness=1, fill=color3)

    dpg.configure_item("mr1b_text", text="S1", pos = (pos1max[0] + 10, (pos1min[1] + pos1max[1])/2 -6), size = 12)
    dpg.configure_item("mr2b_text", text="S2", pos = (pos2max[0] + 10, (pos2min[1] + pos2max[1])/2 -6), size = 12)
    dpg.configure_item("mr3b_text", text="S3", pos = (pos3max[0] + 10, (pos3min[1] + pos3max[1])/2 -6), size = 12)

# updates the data tables
def update_table():
    global mf1, mf2, mf3, isp, table, total_v, payload, bmf1, bmf2, bmf3
    global diameter,height,structural_efficiency,density

    # calculate variables for rocket without booster
    mp = calculate_propellent_mass(height, diameter, density)
    ms = find_structure_mass(structural_efficiency, payload, mp)
    
    v1, v2, v3 = delta_v(mf1, mf2, mf3, isp, payload, ms, mp)
    v1, v2, v3 = round(v1, 2), round(v2, 2), round(v3, 2)
    dv = v1 + v2 + v3
    dv = round(dv, 2)

    mr1, mr2, mr3 = mass_ratios(mf1, mf2, mf3, payload, ms, mp)
    mr1, mr2, mr3 = round(mr1, 3), round(mr2, 3), round(mr3, 3)

    dat = [
        [3, round(mf3,3), mr3, v3],
        [2, round(mf2,3), mr2, v2],
        [1, round(mf1,3), mr1, v1]
    ]

    # update table
    for i in range(2,-1,-1):
        for j in range(3,-1,-1):
            dpg.set_value(table[i][j], str(dat[i][j]))

    dpg.set_value(total_v, f"Delta V: {dv} m/s")

    # repeate for booster stage
    v1, v2, v3 = delta_v(bmf1, bmf2, bmf3, isp, payload, ms, mp)
    v1, v2, v3 = round(v1, 2), round(v2, 2), round(v3, 2)
    dv_booster = v1 + v2 + v3
    dv_booster = round(dv_booster, 2)

    mr1, mr2, mr3 = mass_ratios(bmf1, bmf2, bmf3, payload, ms, mp)
    mr1, mr2, mr3 = round(mr1, 3), round(mr2, 3), round(mr3, 3)

    dat = [
        [3, round(bmf3,3),mr3, v3],
        [2, round(bmf2,3),mr2, v2],
        [1, round(bmf1,3),mr1, v1]
    ]

    for i in range(2,-1,-1):
        for j in range(3,-1,-1):
            dpg.set_value(b_table[i][j], str(dat[i][j]))   
    dpg.set_value(btotal_v, f"Delta V: {dv_booster} m/s") 

    percent_difference = round((dv-dv_booster)/dv * 100,1)
    dpg.set_value(bdifference_v, f"Delta V loss: {percent_difference}%") 

# updates all the graphs
def update_graph():
    global x_propellent, graph_booster_velocity, graph_velocity, heatmap_v

    # clear graph data that isnt set by optimization function
    x_propellent.clear()
    graph_booster_velocity.clear()
    graph_velocity.clear()

    mp = calculate_propellent_mass(height, diameter, density)
    ms = find_structure_mass(structural_efficiency, payload, mp)
    v1, v2, v3 = delta_v(mf1, mf2, mf3, isp, payload,ms, mp)
    bv1, bv2, bv3 = delta_v(bmf1, bmf2, bmf3, isp, payload,ms, mp)

    # update bar graph
    dpg.set_axis_limits("y_bar", 0, v1 + v2 + v3 + (v1 + v2 + v3)/10)
    dpg.configure_item("bar_series_without", x=[10, 20, 30], y=[v1, v1 + v2, v1 + v2 + v3])
    dpg.configure_item("bar_series_with", x=[11, 21, 31],y=[bv1, bv1 + bv2, bv1+bv2+bv3])

    # update trajectory graph
    generate_trajectory(mf1, mf2, mf3, isp, payload,structure_mass, propllent_mass, x_propellent, graph_velocity)
    generate_trajectory(bmf1, bmf2, bmf3, isp, payload,structure_mass, propllent_mass, [], graph_booster_velocity)
    dpg.set_axis_limits("x_axis_traj", min(x_propellent), max(x_propellent))
    dpg.set_axis_limits("y_axis_traj", 0, max(graph_velocity) * 1.3)
    dpg.configure_item("p_without", x = x_propellent, y = graph_velocity)
    dpg.configure_item("p_with", x = x_propellent, y = graph_booster_velocity)

    # update heatmap
    dpg.configure_item("colormap_legend", min_scale = get_lowest_v(), max_scale = max(heatmap_v))
    dpg.configure_item("heat_series", x = heatmap_v, scale_min=get_lowest_v(), scale_max=max(heatmap_v))

    # update booster optimization plot
    dpg.set_axis_limits("y_axis", min(booster_v), max(booster_v) * 1.3)
    dpg.configure_item("booster_optimization", x= booster_ratio, y=booster_v)

# create default optimization
set_constraints(min_fraction, max_fraction)
propllent_mass = calculate_propellent_mass(height, diameter, density)
structure_mass = find_structure_mass(structural_efficiency, payload, propllent_mass)

mf1, mf2, mf3 = optimize_mass_fraction(isp, payload, structure_mass, propllent_mass, heatmap=heatmap_v)
mf1, mf2, mf3 = round(mf1, 3), round(mf2,3), round(mf3,3)
bmf1, bmf2, bmf3 = optimize_booster(isp, payload, structure_mass, propllent_mass, time_to_burn, booster_v=booster_v, booster_ratio=booster_ratio)
bmf1, bmf2, bmf3 = round(bmf1, 3), round(bmf2,3), round(bmf3,3)
generate_trajectory(mf1, mf2, mf3, isp, payload,structure_mass, propllent_mass, x_propellent, graph_velocity)
generate_trajectory(bmf1, bmf2, bmf3, isp, payload,structure_mass, propllent_mass, [], graph_booster_velocity)

# graphs window
with dpg.window(label="Graphs", no_resize=True, no_close=True, no_move=True, no_collapse=True, min_size=[459,472], max_size = [459, 472], pos=[424, 0], no_focus_on_appearing=True) as plots:
    # section with bar and trajectory graphs
    with dpg.tree_node(label = "Velocity Comparisons of Optimized Rockets", default_open = True):
        dpg.add_text("The total velocity after each stage. ")

        # bar series of each stage
        with dpg.plot(label = "V after Stage", no_mouse_pos = True):
            v1, v2, v3 = delta_v(mf1, mf2, mf3, isp, payload,structure_mass, propllent_mass)
            bv1, bv2, bv3 = delta_v(bmf1, bmf2, bmf3, isp, payload,structure_mass, propllent_mass)

            dpg.add_plot_legend()

            # create x axis
            dpg.add_plot_axis(dpg.mvXAxis, label="Stage", no_gridlines=True)
            dpg.set_axis_limits(dpg.last_item(), 9, 33)
            dpg.set_axis_ticks(dpg.last_item(), (("S1", 11), ("S2", 21), ("S3", 31)))
                            
                
            # create y axis
            with dpg.plot_axis(dpg.mvYAxis, label="V (m/s)", tag = "y_bar"):
                dpg.set_axis_limits(dpg.last_item(), 0, v1 + v2 + v3 + (v1 + v2 + v3)/10)

                # plot with and without booster
                dpg.add_bar_series([10, 20, 30], [v1, v1 + v2, v1 + v2 + v3],  tag="bar_series_without", label="Without Booster", weight=1)
                dpg.add_bar_series([11, 21, 31], [bv1, bv1 + bv2, bv1+bv2+bv3], tag="bar_series_with", label="With Booster", weight=1)
        
        dpg.add_text("The total velocity compared to propellent used.")
        # line graph showing the velocity of the rocket as propellent is used
        with dpg.plot(label = "V as propellent is used"):
            dpg.add_plot_legend()
            dpg.add_plot_axis(dpg.mvXAxis, label="Propellent (kg)", tag = "x_axis_traj", lock_min=True, lock_max=True)
            dpg.add_plot_axis(dpg.mvYAxis, label="V (m/s)", tag="y_axis_traj", lock_min=True, lock_max=True)  
            

            dpg.set_axis_limits("x_axis_traj", min(x_propellent), max(x_propellent))
            dpg.set_axis_limits("y_axis_traj", 0, max(graph_velocity) + max(graph_velocity)*0.3)
            dpg.add_line_series(x_propellent, graph_velocity, parent="y_axis_traj", label = "Without Booster", tag = "p_without")
            dpg.add_line_series(x_propellent, graph_booster_velocity, parent="y_axis_traj", label = "With Booster", tag = "p_with")

    # section with optimization graphs
    with dpg.tree_node(label = "Optimization Process", default_open = True):
        dpg.add_text("Without Pop-out Booster")

        # Heat map showing optimization of rocket without booster stage
        with dpg.group(horizontal=True):
            dpg.add_colormap_scale(min_scale=get_lowest_v(), max_scale=max(heatmap_v), height=200, colormap = dpg.mvPlotColormap_Plasma, tag = "colormap_legend")

            # add heatmap showing the velocity for different mass fractions for stage 1 and stage 2
            with dpg.plot(label="V compared to Stage Mass Fraction", no_mouse_pos=True, height=200, width=-1):
                dpg.bind_colormap(dpg.last_item(), dpg.mvPlotColormap_Plasma)  
                dpg.add_plot_axis(dpg.mvXAxis, label="Stage 1 Mass Fraction", lock_min=True, lock_max=True, no_gridlines=True, no_tick_marks=True)
                with dpg.plot_axis(dpg.mvYAxis, label="Stage 2 Mass Fraction", no_gridlines=True, no_tick_marks=True, lock_min=True, lock_max=True):
                    dpg.add_heat_series(heatmap_v, 100, 100, tag="heat_series",scale_min=get_lowest_v(), scale_max=max(heatmap_v), format="")
        
        # line graph showing the change in stage 2 and total delta v
        dpg.add_text("With Pop-out Booster")

        # create a theme for the plot so the color is legable
        with dpg.theme(tag="plot_theme"):
            with dpg.theme_component(dpg.mvLineSeries):
                dpg.add_theme_color(dpg.mvPlotCol_Line, (76, 114, 176), category=dpg.mvThemeCat_Plots)


        with dpg.plot(label = "V compared to Stage Mass Fraction"):
            dpg.add_plot_axis(dpg.mvXAxis, label="Stage 2 Mass Fraction", tag = "x_axis", lock_min=True, lock_max=True)
            dpg.add_plot_axis(dpg.mvYAxis, label="V (m/s)", tag="y_axis", lock_min=True, lock_max=True)  
            

            dpg.set_axis_limits("x_axis", 0, 1)
            dpg.set_axis_limits("y_axis", min(booster_v), max(booster_v) + 1000)

            dpg.add_line_series(booster_ratio, booster_v, parent="y_axis", tag = "booster_optimization")
            dpg.bind_item_theme("booster_optimization", "plot_theme")

# window for settings
with dpg.window(label="Optimization Settings", no_resize=True, no_close=True, no_move=True, no_collapse=True, min_size=[300,150], max_size = [300,150], no_title_bar=False):

    dpg.add_button(label="Update Optimization", callback=on_click)    
    dpg.add_text("Advanced Variables")

    # variables that describe the rockets performance. Defaults are reasonable approximations found using research
    with dpg.tree_node(label="Rocket Constants"):

        dpg.add_input_float(label="ISP (s)", width=100, step=0, default_value=isp, min_clamped=True, min_value=10, tag = "isp")
        dpg.add_input_float(label="Fuel Density (kg/m^3)", width=100, step = 0, default_value=density, min_value=10, min_clamped=True, tag = "density")
        dpg.add_input_float(label="Structural Efficieny", width=100, step = 0, default_value=structural_efficiency, min_value=1, min_clamped=True, tag = "efficiency")

    # vairables that describe the specific problem. Defaults given by the client 
    with dpg.tree_node(label = "Problem Specifications"):
        dpg.add_input_float(label="pay load (kg)", width=100, step = 0, default_value=payload, min_value=0, min_clamped=True, tag = "payload")
        dpg.add_input_float(label="Stack Height (m)", width=100, step = 0, default_value=height, min_value=0.001, min_clamped=True, tag = "height")
        dpg.add_input_float(label="Rocket Diameter (m)", width=100, step = 0, default_value=diameter, min_value=0.001, min_clamped=True, tag = "diameter")
        dpg.add_input_float(label="Pop-out burn time (s)", width=100, step = 0, default_value=time_to_burn, min_value=0.001, min_clamped=True, tag = "burn_time")
    
    # varables that constrain the optimization values. Defaults given by client
    with dpg.tree_node(label = "Constraints"):
        dpg.add_checkbox(label = "Constrain Optimization", default_value = True, tag = "constrained")
        dpg.add_input_float(label = "Min mass fraction", width=100, step = 0, default_value=min_fraction, min_value=0, max_value = 0.331, min_clamped=True, max_clamped = True,tag= "min")
        dpg.add_input_float(label = "Max mass fraction", width=100, step = 0, default_value=max_fraction, min_value=0.335, max_value = 1, min_clamped=True, max_clamped = True, tag = "max")
        

# show the rocket with proportional representations of each stage
with dpg.window(label="Visualizations", no_resize=True, no_close=True, no_move=True, no_collapse=True, min_size=[125,1000], max_size = [125, 1000], pos=[300, 0], no_focus_on_appearing=True):
    # draw mass ratio representations
    dpg.add_text("Optimized Rocket\nWithout Booster")
    with dpg.drawlist(width=191, height=180):
        # Draw a rectangle from (50, 50) to (200, 200)

        # add values but tag are calculated and overriden in update_mass_ratio_fraction
        dpg.draw_rectangle(pmin = 0, pmax = 0, tag = "mr1")
        dpg.draw_rectangle(pmin = 0, pmax = 0, tag = "mr2")
        dpg.draw_rectangle(pmin = 0, pmax = 0, tag = "mr3")

        dpg.draw_text(pos = [0.0], text = "", tag = "mr1_text")
        dpg.draw_text(pos = [0.0], text = "", tag = "mr2_text")
        dpg.draw_text(pos = [0.0], text = "", tag = "mr3_text")

    dpg.add_text("Optimized Rocket\nWith Booster")
    with dpg.drawlist(width=191, height=200):
        # same for booster stage
        dpg.draw_rectangle(pmin = 0, pmax = 0, tag = "mr1b")
        dpg.draw_rectangle(pmin = 0, pmax = 0, tag = "mr2b")
        dpg.draw_rectangle(pmin = 0, pmax = 0, tag = "mr3b")

        dpg.draw_text(pos = [0.0], text = "", tag = "mr1b_text")
        dpg.draw_text(pos = [0.0], text = "", tag = "mr2b_text")
        dpg.draw_text(pos = [0.0], text = "", tag = "mr3b_text")

    update_mass_ratio_fraction()
    

# data table showing velocity, mass fraction and mass ratio for both rockets
with dpg.window(label="Data",no_resize=True, no_close=True, no_move=True, no_collapse=True, min_size=[300,330],max_size=[300,330], pos=[0, 150], no_focus_on_appearing=True):
    dpg.add_text("Optimized Rocket")
    with dpg.table(header_row=True, row_background=True,
                   borders_innerH=True, borders_outerH=True, borders_innerV=True,
                   borders_outerV=True):

        # define columns
        dpg.add_table_column(label = "Stage")
        dpg.add_table_column(label = "MF")
        dpg.add_table_column(label = "MR")
        dpg.add_table_column(label = "V")



        # dummy table (filled by update_table)
        data = [
            [1, 0.1, 100, 0],
            [2, 0.2, 100, 0],
            [3, 0.7, 100, 0]
        ]

        # create and store rable
        for i in range(0, 3):
            with dpg.table_row():
                table.append([])
                for j in range(0, 4):
                    table[-1].append(dpg.add_text(data[i][j]))

    # text showing total delta v
    total_v = dpg.add_text("IF YOU CAN READ THIS IT DIDNT WORK")
    dpg.add_text("Optimized Rocket with Booster Stage")

    # repeat for second rocket
    with dpg.table(header_row=True, row_background=True,
                   borders_innerH=True, borders_outerH=True, borders_innerV=True,
                   borders_outerV=True):

        dpg.add_table_column(label = "Stage")
        dpg.add_table_column(label = "MF")
        dpg.add_table_column(label = "MR")
        dpg.add_table_column(label = "V")



        data = [
            [1, 0.1, 100, 0],
            [2, 0.2, 100, 0],
            [3, 0.7, 100, 0]
        ]

        for i in range(0, 3):
            with dpg.table_row():
                b_table.append([])
                for j in range(0, 4):
                    b_table[-1].append(dpg.add_text(data[i][j]))

    btotal_v = dpg.add_text("IF YOU CAN READ THIS IT DIDNT WORK")
    bdifference_v = dpg.add_text("Delta V loss: 8.1%")
    # update values in table based on optimization
    update_table()


dpg.create_viewport(resizable=False, max_height=510, max_width=900, title="Missile Booster Code")

# light theme used for screenshots of graphs
light_theme = create_theme_imgui_light()
#dpg.bind_theme(light_theme)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context() 