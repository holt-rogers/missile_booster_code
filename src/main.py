import dearpygui.dearpygui as dpg

def save_callback():
    print("Save Clicked")

dpg.create_context()
dpg.create_viewport(resizable=False, max_height=500, max_width=900)
dpg.setup_dearpygui()

time_to_burn = 10
payload = 250


with dpg.window(label="Settings", no_resize=True, no_close=True, no_move=True, no_collapse=True, min_size=[300,250]):
    dpg.add_text("Mass Ratio Optomization For a 3-Stage Rocket")
    dpg.add_checkbox(label="Pop-out booster")
    dpg.add_button(label="Update Optomization", callback=save_callback)

    with dpg.tree_node(label="Advanved Variables"):
        dpg.add_input_float(label="ISP (s)", width=100, step=0)
        dpg.add_input_float(label="pay load (kg)", width=100, step = 0, default_value=payload)
        dpg.add_input_float(label="Pop-out burn time (s)", width=100, step = 0, default_value=time_to_burn)
        




dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()