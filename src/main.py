import dearpygui.dearpygui as dpg
from missile_optimization import optimize_mass_ratio, delta_v




dpg.create_context()


time_to_burn = 10
payload = 250
isp = 300


mass_r1, mass_r2, mass_r3 = optimize_mass_ratio(isp, payload)


table = []
total_v = None



def on_click():
    global mass_r1, mass_r2, mass_r3, isp, payload, time_to_burn, table

    isp = dpg.get_value("isp")
    payload = dpg.get_value("payload")
    time_to_burn = dpg.get_value("burn_time")

    mass_r1, mass_r2, mass_r3 =  optimize_mass_ratio(isp, payload, dpg.get_value("booster_value"), time_to_burn)
    update_mass_ratio_visual()
    update_table()
    


def update_mass_ratio_visual():
    global mass_r1, mass_r2, mass_r3

    pos_x = 10
    pos_y = 10

    width = 30
    height = 150


    pos1min = [pos_x, pos_y]
    pos1max = [pos_x + width, pos_y + mass_r1*height]

    pos2min = [pos_x, pos1max[1]]
    pos2max = [pos_x + width, pos2min[1] + height * mass_r2]

    pos3min = [pos_x, pos2max[1]]
    pos3max = [pos_x + width, pos3min[1] + height * mass_r3]

    border_color = (0,0,0,255)

    color1 = (144, 169, 237, 255)
    color2 = (182, 198, 242, 255)
    color3 = (219, 227, 248, 255)

    dpg.configure_item("mr1", pmin=pos1min, pmax=pos1max, color=border_color, thickness=1, fill=color1)
    dpg.configure_item("mr2", pmin=pos2min, pmax=pos2max, color=border_color, thickness=1, fill=color2)
    dpg.configure_item("mr3", pmin=pos3min, pmax=pos3max, color=border_color, thickness=1, fill=color3)

    dpg.configure_item("mr1_text", text="MR1:", pos = (pos1max[0] + 10, (pos1min[1] + pos1max[1])/2 -6), size = 12)
    dpg.configure_item("mr2_text", text="MR2:", pos = (pos2max[0] + 10, (pos2min[1] + pos2max[1])/2 -6), size = 12)
    dpg.configure_item("mr3_text", text="MR3:", pos = (pos3max[0] + 10, (pos3min[1] + pos3max[1])/2 -6), size = 12)

def update_table():
    global mass_r1, mass_r2, mass_r3, isp, table, total_v

    v1, v2, v3 = delta_v(mass_r1, mass_r2, mass_r3, isp)
    v1, v2, v3 = round(v1, 2), round(v2, 2), round(v3, 2)
    dv = v1 + v2 + v3
    dv = round(dv, 2)

    dat = [
        [1, mass_r1, v1],
        [2, mass_r2, v2],
        [3, mass_r3, v3]
    ]

    for i in range(3):
        for j in range(3):
            dpg.set_value(table[i][j], str(dat[i][j]))

    dpg.set_value(total_v, f"Delta V: {dv}")


def update():
    pass
    
# window for settings
with dpg.window(label="Optomization Settings", no_resize=True, no_close=True, no_move=True, no_collapse=True, min_size=[350,250], no_title_bar=False):
    dpg.add_text("Mass Ratio Optomization For a 3-Stage Rocket")
    dpg.add_checkbox(label="Pop-out booster", tag = "booster_value")
    dpg.add_button(label="Update Optomization", callback=on_click)
    

    with dpg.tree_node(label="Advanved Variables"):
        dpg.add_input_float(label="ISP (s)", width=100, step=0, default_value=isp, min_clamped=True, min_value=0.001, tag = "isp")
        dpg.add_input_float(label="pay load (kg)", width=100, step = 0, default_value=payload, min_value=0, min_clamped=True, tag = "payload")
        dpg.add_input_float(label="Pop-out burn time (s)", width=100, step = 0, default_value=time_to_burn, min_value=0.001, min_clamped=True, tag = "burn_time")
    


with dpg.window(label="Mass Ratio", no_resize=True, no_close=True, no_move=True, no_collapse=True, min_size=[100,250], pos=[0, 250], no_focus_on_appearing=True):
    # draw mass ratio representations
    with dpg.drawlist(width=70, height=250):
        # Draw a rectangle from (50, 50) to (200, 200)

        # add values but tag are calculated and overriden in update_mass_ratio_visual
        dpg.draw_rectangle(pmin = 0, pmax = 0, tag = "mr1")
        dpg.draw_rectangle(pmin = 0, pmax = 0, tag = "mr2")
        dpg.draw_rectangle(pmin = 0, pmax = 0, tag = "mr3")

        dpg.draw_text(pos = [0.0], text = "", tag = "mr1_text")
        dpg.draw_text(pos = [0.0], text = "", tag = "mr2_text")
        dpg.draw_text(pos = [0.0], text = "", tag = "mr3_text")

        update_mass_ratio_visual()
    



with dpg.window(label="Data", no_resize=True, no_close=True, no_move=True, no_collapse=True, min_size=[250,250], pos=[100, 250], no_focus_on_appearing=True):
    
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

     total_v = dpg.add_text("Delta V: 300")
     update_table()
        
    
        


# graphs window
with dpg.window(label="Graphs", no_resize=True, no_close=True, no_move=True, no_collapse=True, min_size=[535,500], pos=[350, 0], no_focus_on_appearing=True):
    pass


dpg.create_viewport(resizable=False, max_height=500, max_width=900, title="Missile Booster Code")
dpg.setup_dearpygui()
dpg.show_viewport()

while dpg.is_dearpygui_running():
    jobs = dpg.get_callback_queue() # retrieves and clears queue
    dpg.run_callbacks(update())
    dpg.render_dearpygui_frame()

dpg.start_dearpygui()
dpg.destroy_context()