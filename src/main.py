import dearpygui.dearpygui as dpg
from missile_optimization import *
from dearpygui_ext.themes import create_theme_imgui_light

#im hacking you rn
dpg.create_context()


time_to_burn = 10
payload = 250
height = 10
diameter = 1
density = 1500 # find source
isp = 300
structural_efficiency = 4


stage_r1, stage_r2, stage_r3 = 0,0,0
bstage_r1, bstage_r2, bstage_r3 = 0.2, 0.5, 0.3

table = []
b_table = []
total_v = None
btotal_v = None

heatmap_v = []

booster_v = []
booster_ratio = []

x_propellent = []
graph_velocity = []
graph_booster_velocity = []

min_ratio = 0.1
max_ratio = 0.8

def on_click():
    global stage_r1, stage_r2, stage_r3, isp, payload, time_to_burn, table, bstage_r1, bstage_r2, bstage_r3
    global diameter, height, density, structural_efficiency, heatmap_v, booster_v, booster_ratio
    
    heatmap_v.clear()
    booster_v.clear()
    booster_ratio.clear()

    isp = dpg.get_value("isp")
    payload = dpg.get_value("payload")
    time_to_burn = dpg.get_value("burn_time")
    density = dpg.get_value("density")
    height = dpg.get_value("height")
    diameter = dpg.get_value("diameter")
    structural_efficiency = dpg.get_value("efficiency")
    min_ratio = dpg.get_value("min")
    max_ratio = dpg.get_value("max")

    if dpg.get_value("constrained"):
        set_constraints(min_ratio, max_ratio)
    else:
        set_constraints(0,1)


    
    propllent_mass = calculate_propellent_mass(height, diameter, density)
    structure_mass = find_structure_mass(structural_efficiency, payload, propllent_mass)

    bstage_r1, bstage_r2, bstage_r3 = optimize_booster(isp, payload, structure_mass, propllent_mass, time_to_burn, booster_v=booster_v, booster_ratio=booster_ratio)
    stage_r1, stage_r2, stage_r3 = optimize_mass_fraction(isp, payload, structure_mass, propllent_mass, heatmap=heatmap_v)
    stage_r1, stage_r2, stage_r3 = round(stage_r1, 3), round(stage_r2,3), round(stage_r3,3)

    update_mass_ratio_visual()
    update_table()
    update_graph()



def update_mass_ratio_visual():
    global stage_r1, stage_r2, stage_r3, bstage_r1, bstage_r2, bstage_r3

    pos_x = 30
    pos_y = 10

    width = 30
    height = 150


    pos3min = [pos_x, pos_y]
    pos3max = [pos_x + width, pos_y + stage_r3*height]

    pos2min = [pos_x, pos3max[1]]
    pos2max = [pos_x + width, pos2min[1] + height * stage_r2]

    pos1min = [pos_x, pos2max[1]]
    pos1max = [pos_x + width, pos1min[1] + height * stage_r1]

    border_color = (0,0,0,255)

    color1 = (144, 169, 237, 255)
    color2 = (182, 198, 242, 255)
    color3 = (219, 227, 248, 255)

    dpg.configure_item("mr1", pmin=pos1min, pmax=pos1max, color=border_color, thickness=1, fill=color1)
    dpg.configure_item("mr2", pmin=pos2min, pmax=pos2max, color=border_color, thickness=1, fill=color2)
    dpg.configure_item("mr3", pmin=pos3min, pmax=pos3max, color=border_color, thickness=1, fill=color3)

    dpg.configure_item("mr1_text", text="S1", pos = (pos1max[0] + 10, (pos1min[1] + pos1max[1])/2 -6), size = 12)
    dpg.configure_item("mr2_text", text="S2", pos = (pos2max[0] + 10, (pos2min[1] + pos2max[1])/2 -6), size = 12)
    dpg.configure_item("mr3_text", text="S3", pos = (pos3max[0] + 10, (pos3min[1] + pos3max[1])/2 -6), size = 12)

    pos3min = [pos_x, pos_y]
    pos3max = [pos_x + width, pos_y + bstage_r3*height]

    pos2min = [pos_x, pos3max[1]]
    pos2max = [pos_x + width, pos2min[1] + height * bstage_r2]

    pos1min = [pos_x, pos2max[1]]
    pos1max = [pos_x + width, pos1min[1] + height * bstage_r1]

    border_color = (0,0,0,255)

    color1 = (144, 169, 237, 255)
    color2 = (182, 198, 242, 255)
    color3 = (219, 227, 248, 255)

    dpg.configure_item("mr1b", pmin=pos1min, pmax=pos1max, color=border_color, thickness=1, fill=color1)
    dpg.configure_item("mr2b", pmin=pos2min, pmax=pos2max, color=border_color, thickness=1, fill=color2)
    dpg.configure_item("mr3b", pmin=pos3min, pmax=pos3max, color=border_color, thickness=1, fill=color3)

    dpg.configure_item("mr1b_text", text="S1", pos = (pos1max[0] + 10, (pos1min[1] + pos1max[1])/2 -6), size = 12)
    dpg.configure_item("mr2b_text", text="S2", pos = (pos2max[0] + 10, (pos2min[1] + pos2max[1])/2 -6), size = 12)
    dpg.configure_item("mr3b_text", text="S3", pos = (pos3max[0] + 10, (pos3min[1] + pos3max[1])/2 -6), size = 12)


def update_table():
    global stage_r1, stage_r2, stage_r3, isp, table, total_v, payload, bstage_r1, bstage_r2, bstage_r3
    global diameter,height,structural_efficiency,density

    mp = calculate_propellent_mass(height, diameter, density)
    ms = find_structure_mass(structural_efficiency, payload, mp)
    #
    v1, v2, v3 = delta_v(stage_r1, stage_r2, stage_r3, isp, payload, ms, mp)
    v1, v2, v3 = round(v1, 2), round(v2, 2), round(v3, 2)
    dv = v1 + v2 + v3
    dv = round(dv, 2)

    mr1, mr2, mr3 = mass_ratios(stage_r1, stage_r2, stage_r3, payload, ms, mp)
    mr1, mr2, mr3 = round(mr1, 3), round(mr2, 3), round(mr3, 3)

    dat = [
        [3, round(stage_r3,3), mr3, v3],
        [2, round(stage_r2,3), mr2, v2],
        [1, round(stage_r1,3), mr1, v1]
    ]

    for i in range(2,-1,-1):
        for j in range(3,-1,-1):
            dpg.set_value(table[i][j], str(dat[i][j]))

    dpg.set_value(total_v, f"Delta V: {dv} m/s")

    v1, v2, v3 = delta_v(bstage_r1, bstage_r2, bstage_r3, isp, payload, ms, mp)
    v1, v2, v3 = round(v1, 2), round(v2, 2), round(v3, 2)
    dv = v1 + v2 + v3
    dv = round(dv, 2)

    mr1, mr2, mr3 = mass_ratios(bstage_r1, bstage_r2, bstage_r3, payload, ms, mp)
    mr1, mr2, mr3 = round(mr1, 3), round(mr2, 3), round(mr3, 3)

    dat = [
        [3, round(bstage_r3,3),mr3, v3],
        [2, round(bstage_r2,3),mr2, v2],
        [1, round(bstage_r1,3),mr1, v1]
    ]

    for i in range(2,-1,-1):
        for j in range(3,-1,-1):
            dpg.set_value(b_table[i][j], str(dat[i][j]))   
    dpg.set_value(btotal_v, f"Delta V: {dv} m/s") 

def update_graph():
    global x_propellent, graph_booster_velocity, graph_velocity, heatmap_v
    x_propellent.clear()
    graph_booster_velocity.clear()
    graph_velocity.clear()

    mp = calculate_propellent_mass(height, diameter, density)
    ms = find_structure_mass(structural_efficiency, payload, mp)
    v1, v2, v3 = delta_v(stage_r1, stage_r2, stage_r3, isp, payload,ms, mp)
    bv1, bv2, bv3 = delta_v(bstage_r1, bstage_r2, bstage_r3, isp, payload,ms, mp)

    dpg.set_axis_limits("y_bar", 0, v1 + v2 + v3 + (v1 + v2 + v3)/10)
    dpg.configure_item("bar_series_without", x=[10, 20, 30], y=[v1, v1 + v2, v1 + v2 + v3])
    dpg.configure_item("bar_series_with", x=[11, 21, 31],y=[bv1, bv1 + bv2, bv1+bv2+bv3])

    generate_trajectory(stage_r1, stage_r2, stage_r3, isp, payload,structure_mass, propllent_mass, x_propellent, graph_velocity)
    generate_trajectory(bstage_r1, bstage_r2, bstage_r3, isp, payload,structure_mass, propllent_mass, [], graph_booster_velocity)

    dpg.set_axis_limits("x_axis_traj", min(x_propellent), max(x_propellent))
    dpg.set_axis_limits("y_axis_traj", 0, max(graph_velocity) * 1.3)
    dpg.configure_item("p_without", x = x_propellent, y = graph_velocity)
    dpg.configure_item("p_with", x = x_propellent, y = graph_booster_velocity)

    dpg.configure_item("colormap_legend", min_scale = get_lowest_v(), max_scale = max(heatmap_v))

    dpg.configure_item("heat_series", x = heatmap_v, scale_min=get_lowest_v(), scale_max=max(heatmap_v))

    dpg.set_axis_limits("y_axis", min(booster_v), max(booster_v) * 1.3)
    dpg.configure_item("booster_optimization", x= booster_ratio, y=booster_v)
    
def update():
    pass

set_constraints(min_ratio, max_ratio)
propllent_mass = calculate_propellent_mass(height, diameter, density)
structure_mass = find_structure_mass(structural_efficiency, payload, propllent_mass)

stage_r1, stage_r2, stage_r3 = optimize_mass_fraction(isp, payload, structure_mass, propllent_mass, heatmap=heatmap_v)
stage_r1, stage_r2, stage_r3 = round(stage_r1, 3), round(stage_r2,3), round(stage_r3,3)
bstage_r1, bstage_r2, bstage_r3 = optimize_booster(isp, payload, structure_mass, propllent_mass, time_to_burn, booster_v=booster_v, booster_ratio=booster_ratio)
bstage_r1, bstage_r2, bstage_r3 = round(bstage_r1, 3), round(bstage_r2,3), round(bstage_r3,3)
generate_trajectory(stage_r1, stage_r2, stage_r3, isp, payload,structure_mass, propllent_mass, x_propellent, graph_velocity)
generate_trajectory(bstage_r1, bstage_r2, bstage_r3, isp, payload,structure_mass, propllent_mass, [], graph_booster_velocity)

# graphs window
with dpg.window(label="Graphs", no_resize=True, no_close=True, no_move=True, no_collapse=True, min_size=[459,460], max_size = [459, 460], pos=[424, 0], no_focus_on_appearing=True) as plots:
    with dpg.tree_node(label = "Velocity Comparisons of Optimized Rockets", default_open = True):
        dpg.add_text("The total velocity after each stage. ")
        with dpg.plot(label = "V after Stage", no_mouse_pos = True):
            v1, v2, v3 = delta_v(stage_r1, stage_r2, stage_r3, isp, payload,structure_mass, propllent_mass)
            bv1, bv2, bv3 = delta_v(bstage_r1, bstage_r2, bstage_r3, isp, payload,structure_mass, propllent_mass)

            dpg.add_plot_legend()

            # create x axis
            dpg.add_plot_axis(dpg.mvXAxis, label="Stage", no_gridlines=True)
            dpg.set_axis_limits(dpg.last_item(), 9, 33)
            dpg.set_axis_ticks(dpg.last_item(), (("S1", 11), ("S2", 21), ("S3", 31)))
                            
                
            # create y axis
            with dpg.plot_axis(dpg.mvYAxis, label="V (m/s)", tag = "y_bar"):

                dpg.set_axis_limits(dpg.last_item(), 0, v1 + v2 + v3 + (v1 + v2 + v3)/10)
                dpg.add_bar_series([10, 20, 30], [v1, v1 + v2, v1 + v2 + v3],  tag="bar_series_without", label="Without Booster", weight=1)
                dpg.add_bar_series([11, 21, 31], [bv1, bv1 + bv2, bv1+bv2+bv3], tag="bar_series_with", label="With Booster", weight=1)
        dpg.add_text("The total velocity compared to propellent used for both rockets.")
        with dpg.plot(label = "V as propellent is used"):
            dpg.add_plot_legend()
            dpg.add_plot_axis(dpg.mvXAxis, label="Propellent (kg)", tag = "x_axis_traj", lock_min=True, lock_max=True)
            dpg.add_plot_axis(dpg.mvYAxis, label="V (m/s)", tag="y_axis_traj", lock_min=True, lock_max=True)  
            

            dpg.set_axis_limits("x_axis_traj", min(x_propellent), max(x_propellent))
            dpg.set_axis_limits("y_axis_traj", 0, max(graph_velocity) + max(graph_velocity)*0.3)
    

            dpg.add_line_series(x_propellent, graph_velocity, parent="y_axis_traj", label = "Without Booster", tag = "p_without")
            dpg.add_line_series(x_propellent, graph_booster_velocity, parent="y_axis_traj", label = "With Booster", tag = "p_with")

    with dpg.tree_node(label = "Optimization Process", default_open = True):
        dpg.add_text("Without Pop-out Booster")
        with dpg.group(horizontal=True):
            dpg.add_colormap_scale(min_scale=get_lowest_v(), max_scale=max(heatmap_v), height=200, colormap = dpg.mvPlotColormap_Plasma, tag = "colormap_legend")
            with dpg.plot(label="V compared to Stage Mass Fraction", no_mouse_pos=True, height=200, width=-1):
                dpg.bind_colormap(dpg.last_item(), dpg.mvPlotColormap_Plasma)  
                dpg.add_plot_axis(dpg.mvXAxis, label="Stage 1 Mass Fraction", lock_min=True, lock_max=True, no_gridlines=True, no_tick_marks=True)
                with dpg.plot_axis(dpg.mvYAxis, label="Stage 2 Mass Fraction", no_gridlines=True, no_tick_marks=True, lock_min=True, lock_max=True):
                    dpg.add_heat_series(heatmap_v, 100, 100, tag="heat_series",scale_min=get_lowest_v(), scale_max=max(heatmap_v), format="")
        dpg.add_text("With Pop-out Booster")

        # create a theme for the plot
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
    #dpg.add_text("Mass Ratio Optomization For a 3-Stage Rocket")
    dpg.add_button(label="Update Optimization", callback=on_click)
    
    dpg.add_text("Advanced Variables")
    with dpg.tree_node(label="Rocket Constants"):

        dpg.add_input_float(label="ISP (s)", width=100, step=0, default_value=isp, min_clamped=True, min_value=10, tag = "isp")
        dpg.add_input_float(label="Fuel Density (kg/m^3)", width=100, step = 0, default_value=density, min_value=10, min_clamped=True, tag = "density")
        dpg.add_input_float(label="Structural Efficieny", width=100, step = 0, default_value=structural_efficiency, min_value=1, min_clamped=True, tag = "efficiency")

    with dpg.tree_node(label = "Problem Specifications"):
        dpg.add_input_float(label="pay load (kg)", width=100, step = 0, default_value=payload, min_value=0, min_clamped=True, tag = "payload")
        dpg.add_input_float(label="Stack Height (m)", width=100, step = 0, default_value=height, min_value=0.001, min_clamped=True, tag = "height")
        dpg.add_input_float(label="Rocket Diameter (m)", width=100, step = 0, default_value=diameter, min_value=0.001, min_clamped=True, tag = "diameter")
        dpg.add_input_float(label="Pop-out burn time (s)", width=100, step = 0, default_value=time_to_burn, min_value=0.001, min_clamped=True, tag = "burn_time")
    
    with dpg.tree_node(label = "Constraints"):
        dpg.add_checkbox(label = "Constrain Optimization", default_value = True, tag = "constrained")
        dpg.add_input_float(label = "Min mass fraction", width=100, step = 0, default_value=min_ratio, min_value=0, max_value = 0.331, min_clamped=True, max_clamped = True,tag= "min")
        dpg.add_input_float(label = "Max mass fraction", width=100, step = 0, default_value=max_ratio, min_value=0.335, max_value = 1, min_clamped=True, max_clamped = True, tag = "max")
        


with dpg.window(label="Visualizations", no_resize=True, no_close=True, no_move=True, no_collapse=True, min_size=[125,1000], max_size = [125, 1000], pos=[300, 0], no_focus_on_appearing=True):
    # draw mass ratio representations
    dpg.add_text("Optimized Rocket\nWithout Booster")
    with dpg.drawlist(width=191, height=180):
        # Draw a rectangle from (50, 50) to (200, 200)

        # add values but tag are calculated and overriden in update_mass_ratio_visual
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

    update_mass_ratio_visual()
    


with dpg.window(label="Data",no_resize=True, no_close=True, no_move=True, no_collapse=True, min_size=[300,310],max_size=[300,310], pos=[0, 150], no_focus_on_appearing=True):
     dpg.add_text("Optimized Rocket")
     with dpg.table(header_row=True, row_background=True,
                   borders_innerH=True, borders_outerH=True, borders_innerV=True,
                   borders_outerV=True):

        # use add_table_column to add columns to the table,
        # table columns use child slot 0
        dpg.add_table_column(label = "Stage")
        dpg.add_table_column(label = "MF")
        dpg.add_table_column(label = "MR")
        dpg.add_table_column(label = "V")

        # add_table_next_column will jump to the next row
        # once it reaches the end of the columns
        # table next column use slot 1


        data = [
            [1, 0.1, 100, 0],
            [2, 0.2, 100, 0],
            [3, 0.7, 100, 0]
        ]

        for i in range(0, 3):
            with dpg.table_row():
                table.append([])
                for j in range(0, 4):
                    table[-1].append(dpg.add_text(data[i][j]))

     total_v = dpg.add_text("IF YOU CAN READ THIS IT DIDNT WORK")

     dpg.add_text("Optimized Rocket with Booster Stage")

     with dpg.table(header_row=True, row_background=True,
                   borders_innerH=True, borders_outerH=True, borders_innerV=True,
                   borders_outerV=True):

        # use add_table_column to add columns to the table,
        # table columns use child slot 0
        dpg.add_table_column(label = "Stage")
        dpg.add_table_column(label = "MF")
        dpg.add_table_column(label = "MR")
        dpg.add_table_column(label = "V")

        # add_table_next_column will jump to the next row
        # once it reaches the end of the columns
        # table next column use slot 1


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
     update_table()

dpg.create_viewport(resizable=False, max_height=500, max_width=900, title="Missile Booster Code")
light_theme = create_theme_imgui_light()
#dpg.bind_theme(light_theme)
dpg.setup_dearpygui()
dpg.show_viewport()

while dpg.is_dearpygui_running():
    jobs = dpg.get_callback_queue() # retrieves and clears queue
    dpg.run_callbacks(update())
    dpg.render_dearpygui_frame()

dpg.start_dearpygui()
dpg.destroy_context() 