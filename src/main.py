import dearpygui.dearpygui as dpg

def save_callback():
    print("Save Clicked")

dpg.create_context()


time_to_burn = 10
payload = 250
isp = 300


def update():

    pass
    
# window for settings
with dpg.window(label="Optomization Settings", no_resize=True, no_close=True, no_move=True, no_collapse=True, min_size=[350,250]):
    dpg.add_text("Mass Ratio Optomization For a 3-Stage Rocket")
    dpg.add_checkbox(label="Pop-out booster")
    dpg.add_button(label="Update Optomization", callback=save_callback)
    

    with dpg.tree_node(label="Advanved Variables"):
        dpg.add_input_float(label="ISP (s)", width=100, step=0, default_value=isp, min_clamped=True, min_value=0.001)
        dpg.add_input_float(label="pay load (kg)", width=100, step = 0, default_value=payload, min_value=0)
        dpg.add_input_float(label="Pop-out burn time (s)", width=100, step = 0, default_value=time_to_burn, min_value=0)


with dpg.window(label="Mass Ratio", no_resize=True, no_close=True, no_move=True, no_collapse=True, min_size=[100,250], pos=[0, 250], no_focus_on_appearing=True):
    # draw mass ratio representations
    with dpg.drawlist(width=70, height=250):
        # Draw a rectangle from (50, 50) to (200, 200)

        pos_x = 10
        pos_y = 10

        width = 30
        height = 150
        mass_r1 = .10
        mass_r2 = .20
        mass_r3 = .70

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

        dpg.draw_rectangle(pmin=pos1min, pmax=pos1max, color=border_color, thickness=1, fill=color1, tag = "mr1")
        dpg.draw_rectangle(pmin=pos2min, pmax=pos2max, color=border_color, thickness=1, fill=color2, tag = "mr2")
        dpg.draw_rectangle(pmin=pos3min, pmax=pos3max, color=border_color, thickness=1, fill=color3, tag = "mr3")

        dpg.draw_text(text="MR1:", pos = (pos1max[0] + 10, (pos1min[1] + pos1max[1])/2 -6), size = 12)
        dpg.draw_text(text="MR2:", pos = (pos2max[0] + 10, (pos2min[1] + pos2max[1])/2 -6), size = 12)
        dpg.draw_text(text="MR3:", pos = (pos3max[0] + 10, (pos3min[1] + pos3max[1])/2 -6), size = 12)


with dpg.window(label="Data", no_resize=True, no_close=True, no_move=True, no_collapse=True, min_size=[250,250], pos=[100, 250], no_focus_on_appearing=True):
     dpg.add_text("Delta V: 300")
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
                for j in range(0, 3):
                    dpg.add_text(data[i][j])
        
    
        


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