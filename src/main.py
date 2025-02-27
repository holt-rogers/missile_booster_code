import dearpygui.dearpygui as dpg

def save_callback():
    print("Save Clicked")

dpg.create_context()
dpg.create_viewport(resizable=False, max_height=500, max_width=900, title="Missile Booster Code")
dpg.setup_dearpygui()

time_to_burn = 10
payload = 250
isp = 0



def update_hover_text():
    """ Update text visibility based on hover state. """
    if dpg.is_item_hovered("rect_tag"):
        dpg.configure_item("hover_text", show=True)
    else:
        dpg.configure_item("hover_text", show=False)

    

with dpg.window(label="Optomization Settings", no_resize=True, no_close=True, no_move=True, no_collapse=True, min_size=[350,250]):
    dpg.add_text("Mass Ratio Optomization For a 3-Stage Rocket")
    dpg.add_checkbox(label="Pop-out booster")
    dpg.add_button(label="Update Optomization", callback=save_callback)
    

    with dpg.tree_node(label="Advanved Variables"):
        dpg.add_input_float(label="ISP (s)", width=100, step=0, default_value=isp)
        dpg.add_input_float(label="pay load (kg)", width=100, step = 0, default_value=payload)
        dpg.add_input_float(label="Pop-out burn time (s)", width=100, step = 0, default_value=time_to_burn)

with dpg.window(label="Results", no_resize=True, no_close=True, no_move=True, no_collapse=True, min_size=[350,250], pos=[0, 250], no_focus_on_appearing=True):
    # draw mass ratio representations
    #with dpg.drawlist(width=300, height=400):
        # Draw a rectangle from (50, 50) to (200, 200)

    pos_x = 15
    pos_y = 15

    width = 30
    height = 180
    mass_r1 = .10
    mass_r2 = .20
    mass_r3 = .70

    pos1min = [pos_x, pos_y]
    pos1max = [pos_x + width, pos_y + mass_r1*height]

    pos2min = [pos_x, pos1max[1]]
    pos2max = [pos_x + width, pos2min[1] + height * mass_r2]

    pos3min = [pos_x, pos2max[1]]
    pos3max = [pos_x + width, pos2min[1] + height * mass_r3]

    border_color = (0,0,0,255)

    color1 = (144, 169, 237, 255)
    color2 = (182, 198, 242, 255)
    color3 = (219, 227, 248, 255)

    dpg.draw_rectangle(pmin=pos1min, pmax=pos1max, color=border_color, thickness=1, fill=color1)

    dpg.draw_rectangle(pmin=pos2min, pmax=pos2max, color=border_color, thickness=1, fill=color2)
    dpg.draw_rectangle(pmin=pos3min, pmax=pos3max, color=border_color, thickness=1, fill=color3)









dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()