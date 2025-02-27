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