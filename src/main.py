import dearpygui.dearpygui as dpg
from missile_optimization import *

#im hacking you rn
dpg.create_context()


time_to_burn = 10
payload = 250
height = 7.5
diameter = .75
density = 1500 # find source
isp = 300
structural_efficiency = 4

graph = None
stage_r1, stage_r2, stage_r3 = 0,0,0
bstage_r1, bstage_r2, bstage_r3 = 0.2, 0.5, 0.3

table = []
total_v = None



def on_click():
    global stage_r1, stage_r2, stage_r3, isp, payload, time_to_burn, table, bstage_r1, bstage_r2, bstage_r3
    global diameter, height, density, structural_efficiency

    isp = dpg.get_value("isp")
    payload = dpg.get_value("payload")
    time_to_burn = dpg.get_value("burn_time")
    density = dpg.get_value("density")
    height = dpg.get_value("height")
    diameter = dpg.get_value("diameter")
    structural_efficiency = dpg.get_value("efficiency")

    
    propllent_mass = calculate_propellent_mass(height, diameter, density)
    structure_mass = find_structure_mass(structural_efficiency, payload, propllent_mass)

    bstage_r1, bstage_r2, bstage_r3 = optimize_booster(isp, payload, structure_mass, propllent_mass, time_to_burn)
    stage_r1, stage_r2, stage_r3 = optimize_mass_ratio(isp, payload, structure_mass, propllent_mass, graph=graph)
    stage_r1, stage_r2, stage_r3 = round(stage_r1, 3), round(stage_r2,3), round(stage_r3,3)
    update_mass_ratio_visual()
    update_table()
    


def update_mass_ratio_visual():
    global stage_r1, stage_r2, stage_r3, bstage_r1, bstage_r2, bstage_r3

    pos_x = 10
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

    pos_x = 110
    pos_y = 10

    width = 30
    height = 150


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

    dpg.configure_item("mr1b_text", text="B", pos = (pos1max[0] + 10, (pos1min[1] + pos1max[1])/2 -6), size = 12)
    dpg.configure_item("mr2b_text", text="S1", pos = (pos2max[0] + 10, (pos2min[1] + pos2max[1])/2 -6), size = 12)
    dpg.configure_item("mr3b_text", text="S2", pos = (pos3max[0] + 10, (pos3min[1] + pos3max[1])/2 -6), size = 12)


def update_table():
    global stage_r1, stage_r2, stage_r3, isp, table, total_v, payload
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
        [3, mr1, v3],
        [2, mr2, v2],
        [1, mr3, v1]
    ]

    for i in range(2,-1,-1):
        for j in range(2,-1,-1):
            dpg.set_value(table[i][j], str(dat[i][j]))

    dpg.set_value(total_v, f"Delta V: {dv} m/s")


def update():
    pass

# graphs window
with dpg.window(label="Graphs", no_resize=True, no_close=True, no_move=True, no_collapse=True, min_size=[535,500], pos=[506, 0], no_focus_on_appearing=True) as plots:
    graph = plots

propllent_mass = calculate_propellent_mass(height, diameter, density)
structure_mass = find_structure_mass(structural_efficiency, payload, propllent_mass)

stage_r1, stage_r2, stage_r3 = optimize_mass_ratio(isp, payload, structure_mass, propllent_mass, graph=graph)
stage_r1, stage_r2, stage_r3 = round(stage_r1, 3), round(stage_r2,3), round(stage_r3,3)
# window for settings
with dpg.window(label="Optomization Settings", no_resize=True, no_close=True, no_move=True, no_collapse=True, min_size=[100,250], no_title_bar=False):
    #dpg.add_text("Mass Ratio Optomization For a 3-Stage Rocket")
    dpg.add_button(label="Update Optomization", callback=on_click)
    
    dpg.add_text("Advanced Variables")
    with dpg.tree_node(label="Rocket Constants"):

        dpg.add_input_float(label="ISP (s)", width=100, step=0, default_value=isp, min_clamped=True, min_value=0.001, tag = "isp")
        dpg.add_input_float(label="Fuel Density (kg/m^3)", width=100, step = 0, default_value=density, min_value=0, min_clamped=True, tag = "density")
        dpg.add_input_float(label="Structural Efficieny", width=100, step = 0, default_value=structural_efficiency, min_value=0.001, min_clamped=True, tag = "efficiency")

    with dpg.tree_node(label = "Problem Specifications"):
        dpg.add_input_float(label="pay load (kg)", width=100, step = 0, default_value=payload, min_value=0, min_clamped=True, tag = "payload")
        dpg.add_input_float(label="Stack Hegith (m)", width=100, step = 0, default_value=height, min_value=0, min_clamped=True, tag = "height")
        dpg.add_input_float(label="Rocket Diameter (m)", width=100, step = 0, default_value=diameter, min_value=0, min_clamped=True, tag = "diameter")
        dpg.add_input_float(label="Pop-out burn time (s)", width=100, step = 0, default_value=time_to_burn, min_value=0.001, min_clamped=True, tag = "burn_time")
    
    with dpg.tree_node(label = "Constraints"):
        dpg.add_input_float(label = "Minimum stage proportion: ")
        dpg.add_input_float(label = "Maximum stage proportion: ")
        


with dpg.window(label="Rocket Visualizations", no_resize=True, no_close=True, no_move=True, no_collapse=True, min_size=[150,250], pos=[0, 250], no_focus_on_appearing=True):
    # draw mass ratio representations
    with dpg.drawlist(width=191, height=200):
        # Draw a rectangle from (50, 50) to (200, 200)

        # add values but tag are calculated and overriden in update_mass_ratio_visual
        dpg.draw_rectangle(pmin = 0, pmax = 0, tag = "mr1")
        dpg.draw_rectangle(pmin = 0, pmax = 0, tag = "mr2")
        dpg.draw_rectangle(pmin = 0, pmax = 0, tag = "mr3")

        dpg.draw_text(pos = [0.0], text = "", tag = "mr1_text")
        dpg.draw_text(pos = [0.0], text = "", tag = "mr2_text")
        dpg.draw_text(pos = [0.0], text = "", tag = "mr3_text")

        # same for booster stage
        dpg.draw_rectangle(pmin = 0, pmax = 0, tag = "mr1b")
        dpg.draw_rectangle(pmin = 0, pmax = 0, tag = "mr2b")
        dpg.draw_rectangle(pmin = 0, pmax = 0, tag = "mr3b")

        dpg.draw_text(pos = [0.0], text = "", tag = "mr1b_text")
        dpg.draw_text(pos = [0.0], text = "", tag = "mr2b_text")
        dpg.draw_text(pos = [0.0], text = "", tag = "mr3b_text")

        update_mass_ratio_visual()
    



with dpg.window(label="Data", no_resize=True, no_close=True, no_move=True, no_collapse=True, min_size=[300,500],max_size=[300,500], pos=[207, 0], no_focus_on_appearing=True, no_scrollbar = True):
     dpg.add_text("Optimized Rocket")
     with dpg.table(header_row=True, row_background=True,
                   borders_innerH=True, borders_outerH=True, borders_innerV=True,
                   borders_outerV=True):

        # use add_table_column to add columns to the table,
        # table columns use child slot 0
        dpg.add_table_column(label = "Stage")
        dpg.add_table_column(label = "MR")
        dpg.add_table_column(label = "V")

        # add_table_next_column will jump to the next row
        # once it reaches the end of the columns
        # table next column use slot 1


        data = [
            [1, 0.1, 100],
            [2, 0.2, 100],
            [3, 0.7, 100]
        ]

        for i in range(0, 3):
            with dpg.table_row():
                table.append([])
                for j in range(0, 3):
                    table[-1].append(dpg.add_text(data[i][j]))

     total_v = dpg.add_text("IF YOU CAN READ THIS IT DIDNT WORK")
     update_table()

     dpg.add_text("Optimized Rocket with Booster Stage")

     with dpg.table(header_row=True, row_background=True,
                   borders_innerH=True, borders_outerH=True, borders_innerV=True,
                   borders_outerV=True):

        # use add_table_column to add columns to the table,
        # table columns use child slot 0
        dpg.add_table_column(label = "Stage")
        dpg.add_table_column(label = "MR")
        dpg.add_table_column(label = "V")

        # add_table_next_column will jump to the next row
        # once it reaches the end of the columns
        # table next column use slot 1


        data = [
            [1, 0.1, 100],
            [2, 0.2, 100],
            [3, 0.7, 100]
        ]

        for i in range(0, 3):
            with dpg.table_row():
                table.append([])
                for j in range(0, 3):
                    table[-1].append(dpg.add_text(data[i][j]))

     total_v = dpg.add_text("IF YOU CAN READ THIS IT DIDNT WORK")
     update_table()    
        




dpg.create_viewport(resizable=False, max_height=500, max_width=900, title="Missile Booster Code")
dpg.setup_dearpygui()
dpg.show_viewport()

while dpg.is_dearpygui_running():
    jobs = dpg.get_callback_queue() # retrieves and clears queue
    dpg.run_callbacks(update())
    dpg.render_dearpygui_frame()

dpg.start_dearpygui()
dpg.destroy_context() 